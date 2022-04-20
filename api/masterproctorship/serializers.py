from collections import OrderedDict

from django.db import transaction
from rest_framework import serializers

from api.feedback.models import Rating
from api.masterproctorship.models import (
    AttendanceFormMasterProctorShip,
    InvoiceMasterProctorShip,
    MasterProctorship,
    MasterProctorShipConstantData,
    MasterProctorshipFeedback,
    MasterProctorshipProctorReport,
    MasterProctorshipProctors,
    MasterProctorshipProposal,
    MasterProctorshipStatus,
    MasterProctorshipTraineeProfile,
)
from api.proctors.serializers import Proctors
from api.proctorship.serializers import ConstantData
from api.serializers import Hospital, Products
from api.status.serializers import StatusConstantData
from api.users.serializers import User
from api.zone.serializers import Countries
from cspro.utils import activity_id


class MasterProctorshipSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField(read_only=True)
    country = serializers.SerializerMethodField(read_only=True)
    hospital = serializers.SerializerMethodField(read_only=True)
    note = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    reason = serializers.CharField(required=True, allow_blank=True, allow_null=True)
    master_proctorship_type = serializers.CharField(
        required=True, allow_null=True, allow_blank=True
    )
    note_related_to_proctor = serializers.CharField(
        required=False, allow_null=True, allow_blank=True
    )
    hotel = serializers.CharField(required=True)
    number_of_cases = serializers.IntegerField(required=True, allow_null=True)
    transplant_time = serializers.CharField(
        required=True, allow_blank=True, allow_null=True
    )
    start_date = serializers.DateField(write_only=True)
    end_date = serializers.DateField(write_only=True)
    user_id = serializers.IntegerField(write_only=True)
    country_id = serializers.IntegerField(write_only=True)
    hospital_id = serializers.IntegerField(write_only=True)
    proctors_id = serializers.ListField(write_only=True)
    trainee_profile = serializers.ListField(write_only=True)

    class Meta:
        model = MasterProctorship
        fields = [
            "id",
            "user",
            "country",
            "hospital",
            "note",
            "reason",
            "master_proctorship_type",
            "note_related_to_proctor",
            "hotel",
            "number_of_cases",
            "transplant_time",
            "start_date",
            "end_date",
            "user_id",
            "country_id",
            "hospital_id",
            "proctors_id",
            "trainee_profile",
        ]

    def create(self, validated_data):
        try:
            with transaction.atomic():
                master_proctorship_type = validated_data.pop("master_proctorship_type")
                start_date = validated_data.pop("start_date")
                end_date = validated_data.pop("end_date")
                user_id = validated_data.pop("user_id")
                trainee = validated_data.pop("trainee_profile")
                proctor_id = validated_data.pop("proctors_id")
                validated_data["user_id"] = user_id
                note_related_to_proctor = validated_data.pop("note_related_to_proctor")
                masterproctorship = MasterProctorship.objects.create(**validated_data)

                num = masterproctorship.id
                char = "MP"
                masterproctorship.activity_id = activity_id(char, num)

                if master_proctorship_type:
                    masterproctorship.master_proctorship_type = (
                        MasterProctorShipConstantData.objects.get(
                            code=master_proctorship_type
                        )
                    )

                for trainee_profile in trainee:
                    MasterProctorshipTraineeProfile.objects.create(
                        master_proctorship=masterproctorship,
                        name=trainee_profile["name"],
                        surname=trainee_profile["surname"],
                        title=ConstantData.objects.get(code=trainee_profile["title"]),
                        mvr_case_per_year=trainee_profile["mvr_case_per_year"],
                        current_preferential=ConstantData.objects.get(
                            code=trainee_profile["current_preferential"]
                        ),
                        mvr_case_per_year_by_trainee=trainee_profile[
                            "mvr_case_per_year_by_trainee"
                        ],
                        note=trainee_profile["note"],
                        corcym_accompanying_rep=trainee_profile[
                            "corcym_accompanying_rep"
                        ],
                        country=Countries.objects.get(id=trainee_profile["country_id"]),
                        hospital=Hospital.objects.get(
                            id=trainee_profile["hospital_id"]
                        ),
                        interest_invasive=trainee_profile["interest_invasive"],
                    )

                status_data = {
                    "status": StatusConstantData.objects.get(code="pending"),
                    "master_proctorship_activity": masterproctorship,
                    "user": User.objects.get(id=user_id),
                }
                status_data = MasterProctorshipStatus.objects.create(**status_data)
                if start_date and end_date:
                    dates = {
                        "start_date": start_date,
                        "end_date": end_date,
                        "status": status_data,
                    }
                    dates = MasterProctorshipProposal.objects.create(**dates)

                if proctor_id:
                    for each in range(len(proctor_id)):
                        proctors = {
                            "master_proctorship_proposal": dates,
                            "proctors": Proctors.objects.get(id=proctor_id[each]),
                            "proctor_order": each + 1,
                            "note_related_to_proctor": note_related_to_proctor,
                        }
                        MasterProctorshipProctors.objects.create(**proctors)

                masterproctorship.save()
                return masterproctorship
        except Exception as e:
            return e

    def get_user(self, obj):
        try:
            return obj.user.name
        except:
            return None

    def get_country(self, obj):
        try:
            return obj.country.name
        except:
            return None

    def get_hospital(self, obj):
        try:
            return obj.hospital.name
        except:
            return None


class MasterProctorshipProctorsSerializer(serializers.ModelSerializer):
    proctors = serializers.SerializerMethodField(read_only=True)
    status = serializers.BooleanField(read_only=True)
    proctor_order = serializers.IntegerField(read_only=True)

    class Meta:
        model = MasterProctorshipProctors
        fields = ["proctors", "status", "proctor_order"]

    def get_proctors(self, obj):
        try:
            return obj.proctors.user.name
        except:
            return None


class MasterProctorshipProposalSerializer(serializers.ModelSerializer):
    proctor_user = serializers.IntegerField(write_only=True)
    start_date = serializers.DateField(required=True)
    end_date = serializers.DateField(required=True)
    note = serializers.CharField(required=True, allow_null=True, allow_blank=True)
    proctors = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = MasterProctorshipProposal
        fields = ["id", "proctor_user", "note", "end_date", "start_date", "proctors"]

    def get_proctor_user(self, obj):
        try:
            return obj.get_proctor_user.name
        except:
            return None

    def get_user(self, obj):
        try:
            return obj.user.name
        except:
            return None


class MasterProctorshipProposalViewSerializer(serializers.ModelSerializer):
    # user = serializers.SerializerMethodField(read_only = True)
    proctor = serializers.SerializerMethodField(read_only=True)
    start_date = serializers.DateField(required=True)
    end_date = serializers.DateField(required=True)
    note = serializers.CharField(required=True, allow_null=True, allow_blank=True)

    class Meta:
        model = MasterProctorshipProposal
        fields = ["id", "proctor", "note", "end_date", "start_date"]

    def get_proctor(self, obj):
        try:
            return MasterProctorshipProctorsSerializer(
                obj.master_proctorship_porposal.all(), many=True
            ).data
        except:
            return None


class MasterProctorshipStatusSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField(read_only=True)
    status = serializers.CharField(required=True)
    user_id = serializers.IntegerField(write_only=True)
    master_proctorship_activity_id = serializers.IntegerField(write_only=True)
    date = serializers.DateField(read_only=True)
    alternatives = serializers.SerializerMethodField(read_only=True)
    alternatives_data = MasterProctorshipProposalSerializer(required=False)
    code = serializers.CharField(read_only=True)
    reason = serializers.CharField(required=False)

    class Meta:
        model = MasterProctorshipStatus
        fields = [
            "id",
            "user",
            "status",
            "user_id",
            "reason",
            "master_proctorship_activity_id",
            "code",
            "date",
            "alternatives",
            "alternatives_data",
        ]

    def create(self, validated_data):
        try:
            with transaction.atomic():
                alternatives_data = OrderedDict()
                if "alternatives_data" in validated_data.keys():
                    alternatives_data = validated_data.pop("alternatives_data")

                master_proctorship_activity_id = validated_data.pop(
                    "master_proctorship_activity_id"
                )
                validated_data[
                    "master_proctorship_activity_id"
                ] = master_proctorship_activity_id

                MasterProctorshipStatus.objects.filter(
                    master_proctorship_activity__id=master_proctorship_activity_id
                ).update(is_active=False)
                status = validated_data.pop("status")
                user_id = validated_data.pop("user_id")
                validated_data["user_id"] = user_id
                validated_data["status"] = StatusConstantData.objects.get(code=status)
                status = MasterProctorshipStatus.objects.create(**validated_data)

                if len(alternatives_data) != 0:
                    data_add = {
                        "status": status,
                        "note": alternatives_data["note"],
                        "start_date": alternatives_data["start_date"],
                        "end_date": alternatives_data["end_date"],
                    }
                    alt = MasterProctorshipProposal.objects.create(**data_add)
                    if "proctor_user" in alternatives_data.keys():
                        qs = MasterProctorshipProctors.objects.filter(
                            master_proctorship_proposal__status__master_proctorship_activity__id=master_proctorship_activity_id,
                            status=True,
                        )
                        if qs:
                            qs.update(status=False)
                        proctors = {
                            "master_proctorship_proposal": alt,
                            "proctors": Proctors.objects.get(
                                id=alternatives_data["proctor_user"]
                            ),
                            "proctor_order": 1,
                        }
                        alpha = MasterProctorshipProctors.objects.create(**proctors)

                status.save()
                return status
        except Exception as e:
            return e

    def get_user(self, obj):
        try:
            return obj.user.name
        except:
            return None

    def get_alternatives(self, obj):
        try:
            return MasterProctorshipProposalViewSerializer(
                obj.alter_proctorship_porposal.get()
            ).data
        except:
            return None


class MasterProctorshipStatusViewSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField(read_only=True)
    status = serializers.SerializerMethodField(read_only=True)
    code = serializers.SerializerMethodField(read_only=True)
    date = serializers.DateField(read_only=True)
    reason = serializers.CharField(read_only=True)
    alternatives = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = MasterProctorshipStatus
        fields = ["id", "user", "status", "code", "date", "alternatives", "reason"]

    def get_user(self, obj):
        try:
            return obj.user.name
        except:
            return None

    def get_alternatives(self, obj):
        try:
            return MasterProctorshipProposalViewSerializer(
                obj.alter_master_proctorship_porposal.get()
            ).data
        except:
            return None

    def get_status(self, obj):
        try:
            return obj.status.name
        except:
            return None

    def get_code(self, obj):
        try:
            return obj.status.code
        except:
            return None


class MasterProctorshipViewSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField(read_only=True)
    country = serializers.SerializerMethodField(read_only=True)
    hospital = serializers.SerializerMethodField(read_only=True)
    country_id = serializers.SerializerMethodField(read_only=True)
    hospital_id = serializers.SerializerMethodField(read_only=True)
    note = serializers.CharField(read_only=True)
    reason = serializers.CharField(read_only=True)
    master_proctorship_type = serializers.SerializerMethodField(read_only=True)
    hotel = serializers.CharField(read_only=True)
    number_of_cases = serializers.IntegerField(read_only=True)
    transplant_time = serializers.CharField(read_only=True)
    status = serializers.SerializerMethodField(read_only=True)
    activity_id = serializers.CharField(read_only=True)

    class Meta:
        model = MasterProctorship
        fields = [
            "id",
            "user",
            "country",
            "hospital",
            "note",
            "reason",
            "master_proctorship_type",
            "hotel",
            "number_of_cases",
            "transplant_time",
            "status",
            "hospital_id",
            "country_id",
            "activity_id",
        ]

    def get_user(self, obj):
        try:
            return obj.user.name
        except:
            return None

    def get_country(self, obj):
        try:
            return obj.country.name
        except:
            return None

    def get_hospital_id(self, obj):
        try:
            return obj.hospital.id
        except:
            return None

    def get_country_id(self, obj):
        try:
            return obj.country.id
        except:
            return None

    def get_hospital(self, obj):
        try:
            return obj.hospital.hospital_name
        except:
            return None

    def get_status(self, obj):
        try:
            return MasterProctorshipStatusViewSerializer(
                obj.master_proctorship_status.all(), many=True
            ).data
        except:
            return None

    def get_master_proctorship_type(self, obj):
        try:
            return obj.master_proctorship_type.name
        except:
            return None


class TraineeMasterProctorshipSerializer(serializers.ModelSerializer):
    master_proctorship_id = serializers.IntegerField(write_only=True)
    title = serializers.CharField(required=True)
    name = serializers.CharField(required=True)
    surname = serializers.CharField(required=True)
    corcym_accompanying_rep = serializers.CharField(required=True)
    current_preferential = serializers.CharField(required=True)
    mvr_case_per_year = serializers.IntegerField(required=True)
    mvr_case_per_year_by_trainee = serializers.IntegerField(required=True)
    note = serializers.CharField(required=True, allow_null=True, allow_blank=True)
    hospital = serializers.SerializerMethodField(read_only=True)
    hospital_id = serializers.IntegerField(write_only=True)
    country = serializers.SerializerMethodField(read_only=True)
    country_id = serializers.IntegerField(write_only=True)
    status = serializers.BooleanField(read_only=True)
    interest_invasive = serializers.BooleanField(required=True)
    revoke = serializers.BooleanField(read_only=True)

    class Meta:
        model = MasterProctorshipTraineeProfile
        fields = [
            "id",
            "status",
            "master_proctorship_id",
            "interest_invasive",
            "revoke",
            "hospital",
            "hospital_id",
            "country",
            "country_id",
            "title",
            "name",
            "surname",
            "corcym_accompanying_rep",
            "current_preferential",
            "mvr_case_per_year",
            "mvr_case_per_year_by_trainee",
            "note",
        ]

    def create(self, validated_data):
        try:
            with transaction.atomic():
                title = validated_data.pop("title")
                current_preferential = validated_data.pop("current_preferential")
                trainee = MasterProctorshipTraineeProfile.objects.create(
                    **validated_data
                )
                trainee.title = ConstantData.objects.get(code=title)
                trainee.current_preferential = ConstantData.objects.get(
                    code=current_preferential
                )
                trainee.save()
                return trainee
        except Exception as e:
            return str(e)

    def get_hospital(self, obj):
        try:
            return obj.hospital.hospital_name
        except:
            return None

    def get_country(self, obj):
        try:
            return obj.country.name
        except:
            return None


class TraineeMasterUpdateProctorshipSerializer(serializers.ModelSerializer):
    title = serializers.CharField(required=False)
    name = serializers.CharField(required=False)
    surname = serializers.CharField(required=False)
    corcym_accompanying_rep = serializers.CharField(required=False)
    current_preferential = serializers.CharField(required=False)
    mvr_case_per_year = serializers.IntegerField(required=False)
    mvr_case_per_year_by_trainee = serializers.IntegerField(required=False)
    note = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    status = serializers.BooleanField(read_only=True)
    interest_invasive = serializers.BooleanField(required=False)

    class Meta:
        model = MasterProctorshipTraineeProfile
        fields = [
            "id",
            "status",
            "interest_invasive",
            "revoke",
            "title",
            "name",
            "surname",
            "corcym_accompanying_rep",
            "current_preferential",
            "mvr_case_per_year",
            "mvr_case_per_year_by_trainee",
            "note",
        ]

    def update(self, instance, validated_data):
        instance.name = validated_data.get("name", instance.name)
        instance.surname = validated_data.get("surname", instance.surname)
        if "title" in validated_data.keys():
            title = validated_data.pop("title")
            validated_data["title"] = ConstantData.objects.get(code=title)
            instance.title = validated_data.get("title", instance.title)

        instance.corcym_accompanying_rep = validated_data.get(
            "corcym_accompanying_rep", instance.corcym_accompanying_rep
        )
        if "current_preferential" in validated_data.keys():
            current_preferential = validated_data.pop("current_preferential")
            validated_data["current_preferential"] = ConstantData.objects.get(
                code=current_preferential
            )
            instance.current_preferential = validated_data.get(
                "current_preferential", instance.current_preferential
            )
        instance.mvr_case_per_year = validated_data.get(
            "mvr_case_per_year", instance.mvr_case_per_year
        )
        instance.mvr_case_per_year_by_trainee = validated_data.get(
            "mvr_case_per_year_by_trainee", instance.mvr_case_per_year_by_trainee
        )
        instance.note = validated_data.get("note", instance.note)
        instance.interest_invasive = validated_data.get(
            "interest_invasive", instance.interest_invasive
        )
        instance.save()
        return instance


class MasterProctorShipConstantDataSerializers(serializers.ModelSerializer):
    name = serializers.CharField(read_only=True)
    code = serializers.CharField(read_only=True)

    class Meta:
        model = MasterProctorShipConstantData
        fields = ["name", "code"]


class MasterProctorshipProctorReportSerializers(serializers.ModelSerializer):
    master_proctorship_trainee_id = serializers.IntegerField(required=True)
    num_of_patients = serializers.IntegerField(required=True)
    num_of_perceval = serializers.IntegerField(required=True)
    rate_of_experince = serializers.CharField(required=True)
    have_difficulties = serializers.BooleanField(required=True)
    need_for_further_training = serializers.BooleanField(required=True)
    corcym_suggestion = serializers.CharField(required=True)
    proctor_report = serializers.FileField(required=True)

    class Meta:
        model = MasterProctorshipProctorReport
        fields = [
            "master_proctorship_trainee_id",
            "num_of_patients",
            "num_of_perceval",
            "rate_of_experince",
            "have_difficulties",
            "need_for_further_training",
            "corcym_suggestion",
            "proctor_report",
        ]

    def create(self, validated_data):
        try:
            with transaction.atomic():
                rate_of_experince = validated_data.pop("rate_of_experince")
                proctor_report = MasterProctorshipProctorReport.objects.create(
                    **validated_data
                )
                proctor_report.rate_of_experince = Rating.objects.get(
                    code=rate_of_experince
                )
                proctor_report.save()
                return proctor_report
        except Exception as e:
            return e


class MasterProctorshipProctorUpdateReportSerializers(serializers.ModelSerializer):
    num_of_patients = serializers.IntegerField(required=False)
    num_of_perceval = serializers.IntegerField(required=False)
    rate_of_experince = serializers.CharField(required=False)
    have_difficulties = serializers.BooleanField(required=False)
    need_for_further_training = serializers.BooleanField(required=False)
    corcym_suggestion = serializers.CharField(required=False)
    proctor_report = serializers.FileField(required=False)

    class Meta:
        model = MasterProctorshipProctorReport
        fields = [
            "num_of_patients",
            "num_of_perceval",
            "rate_of_experince",
            "have_difficulties",
            "need_for_further_training",
            "corcym_suggestion",
            "proctor_report",
        ]

    def update(self, instance, validated_data):
        try:
            rate_of_experince = validated_data.pop("rate_of_experince")
            instance.num_of_patients = validated_data.get(
                "num_of_patients", instance.num_of_patients
            )
            instance.num_of_perceval = validated_data.get(
                "num_of_perceval", instance.num_of_perceval
            )
            instance.rate_of_experince = validated_data.get(
                "rate_of_experince", instance.rate_of_experince
            )
            instance.have_difficulties = validated_data.get(
                "have_difficulties", instance.have_difficulties
            )
            instance.need_for_further_training = validated_data.get(
                "need_for_further_training", instance.need_for_further_training
            )
            instance.corcym_suggestion = validated_data.get(
                "corcym_suggestion", instance.corcym_suggestion
            )
            instance.proctor_report = validated_data.get(
                "proctor_report", instance.proctor_report
            )
            instance.save()
            return instance
        except Exception as e:
            return e


class MasterProctorshipFeedbackSerializers(serializers.ModelSerializer):
    master_proctorship_activity_id = serializers.IntegerField(required=True)
    num_of_patients = serializers.IntegerField(required=True)
    rate_of_proceduresc = serializers.CharField(required=True)
    new_proctor_need_further_training = serializers.BooleanField(required=True)
    suggestion = serializers.CharField(required=True)
    report = serializers.FileField(required=True)
    rate_proctoring_experince = serializers.CharField(required=True)
    rate_of_level_support = serializers.CharField(required=True)

    class Meta:
        model = MasterProctorshipFeedback
        fields = [
            "master_proctorship_activity_id",
            "num_of_patients",
            "rate_of_proceduresc",
            "rate_proctoring_experince",
            "rate_of_level_support",
            "new_proctor_need_further_training",
            "suggestion",
            "report",
        ]

    def create(self, validated_data):
        try:
            with transaction.atomic():
                rate_of_level_support_code = validated_data.pop("rate_of_level_support")
                rate_proctoring_experince_code = validated_data.pop(
                    "rate_proctoring_experince"
                )
                feedback = MasterProctorshipFeedback.objects.create(**validated_data)
                feedback.rate_of_level_support = Rating.objects.get(
                    code=rate_of_level_support_code
                )
                feedback.rate_proctoring_experince = Rating.objects.get(
                    code=rate_proctoring_experince_code
                )
                feedback.save()
                return feedback
        except Exception as e:
            return e


class MasterProctorshipUpdateFeedbackSerializers(serializers.ModelSerializer):
    num_of_patients = serializers.IntegerField(required=False)
    rate_of_proceduresc = serializers.CharField(read_only=False)
    new_proctor_need_further_training = serializers.BooleanField(required=False)
    suggestion = serializers.CharField(required=False)
    report = serializers.FileField(required=False)
    rate_proctoring_experince = serializers.SerializerMethodField(read_only=False)
    rate_of_level_support = serializers.SerializerMethodField(read_only=False)

    class Meta:
        model = MasterProctorshipFeedback
        fields = [
            "master_proctorship_activity",
            "num_of_patients",
            "rate_of_proceduresc",
            "rate_proctoring_experince",
            "rate_of_level_support",
            "new_proctor_need_further_training",
            "suggestion",
            "report",
        ]

    def update(self, instance, validated_data):
        try:
            if "rate_of_level_support" in validated_data.keys():
                validated_data["rate_of_level_support"] = Rating.objects.get(
                    code=validated_data.pop("rate_of_level_support")
                )
                instance.rate_of_level_support = validated_data.get(
                    "rate_of_level_support", instance.rate_of_level_support
                )

            if "rate_proctoring_experince" in validated_data.keys():
                validated_data["rate_proctoring_experince"] = Rating.objects.get(
                    code=validated_data.pop("rate_proctoring_experince")
                )
                instance.rate_proctoring_experince = validated_data.get(
                    "rate_proctoring_experince", instance.rate_proctoring_experince
                )

            instance.num_of_patients = validated_data.get(
                "num_of_patients", instance.num_of_patients
            )
            instance.rate_of_proceduresc = validated_data.get(
                "rate_of_proceduresc", instance.rate_of_proceduresc
            )
            instance.new_proctor_need_further_training = validated_data.get(
                "new_proctor_need_further_training",
                instance.new_proctor_need_further_training,
            )
            instance.suggestion = validated_data.get("suggestion", instance.suggestion)
            if "report" in validated_data.keys():
                instance.report = validated_data.get("report", instance.report)

            instance.save()
            return instance
        except Exception as e:
            return e


class MProposalDateUpdateSerializer(serializers.ModelSerializer):
    start_date = serializers.DateField(required=True)
    end_date = serializers.DateField(required=True)

    class Meta:
        model = MasterProctorshipProposal
        fields = ["start_date", "end_date"]

    def update(self, instance, validated_data):
        try:
            instance.start_date = validated_data.get("start_date", instance.start_date)
            instance.end_date = validated_data.get("end_date", instance.end_date)
            instance.save()
            return instance
        except Exception as e:
            return e


class MasterProctorshipListingSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField(read_only=True)
    country = serializers.SerializerMethodField(read_only=True)
    hospital = serializers.SerializerMethodField(read_only=True)
    country_id = serializers.SerializerMethodField(read_only=True)
    hospital_id = serializers.SerializerMethodField(read_only=True)
    note = serializers.CharField(read_only=True)
    reason = serializers.CharField(read_only=True)
    master_proctorship_type = serializers.SerializerMethodField(read_only=True)
    hotel = serializers.CharField(read_only=True)
    number_of_cases = serializers.IntegerField(read_only=True)
    transplant_time = serializers.CharField(read_only=True)
    status = serializers.SerializerMethodField(read_only=True)
    proctor = serializers.SerializerMethodField(read_only=True)
    date = serializers.SerializerMethodField(read_only=True)
    activity_id = serializers.CharField(read_only=True)
    cognos_id = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = MasterProctorship
        fields = [
            "id",
            "user",
            "country",
            "hospital",
            "note",
            "reason",
            "master_proctorship_type",
            "hotel",
            "number_of_cases",
            "transplant_time",
            "hospital_id",
            "country_id",
            "status",
            "proctor",
            "date",
            "activity_id",
            "cognos_id",
        ]

    def get_user(self, obj):
        try:
            return obj.user.name
        except:
            return None

    def get_cognos_id(self, obj):
        try:
            return obj.hospital.cognos_id
        except:
            return None

    def get_country(self, obj):
        try:
            return obj.country.name
        except:
            return None

    def get_hospital_id(self, obj):
        try:
            return obj.hospital.id
        except:
            return None

    def get_country_id(self, obj):
        try:
            return obj.country.id
        except:
            return None

    def get_hospital(self, obj):
        try:
            return obj.hospital.hospital_name
        except:
            return None

    def get_master_proctorship_type(self, obj):
        try:
            return obj.master_proctorship_type.name
        except:
            return None

    def get_status(self, obj):
        try:
            return MasterProctorshipStatusViewSerializer(
                obj.master_proctorship_status.latest("timestamp")
            ).data["code"]
        except:
            return None

    def get_proctor(self, obj):
        try:

            return MasterProctorshipProctorsSerializer(
                obj.master_proctorship_status.filter(
                    alter_master_proctorship_porposal__isnull=False
                )
                .latest("created_on")
                .alter_master_proctorship_porposal.filter(
                    master_proctorship_porposal__isnull=False
                )
                .latest("created_on")
                .master_proctorship_porposal.filter(status=True),
                many=True,
            ).data
        except:
            return None

    def get_date(self, obj):
        try:

            return (
                obj.master_proctorship_status.filter(
                    alter_master_proctorship_porposal__isnull=False
                )
                .latest("created_on")
                .alter_master_proctorship_porposal.get()
                .start_date
            )
        except:
            return None


class InvoiceMasterProctorshipSerializer(serializers.ModelSerializer):
    master_proctorship_id = serializers.IntegerField(write_only=True)
    invoice_number = serializers.CharField(required=True)
    fee_covered = serializers.CharField(required=True)
    other_cost = serializers.CharField(required=True)
    invoice_date = serializers.DateField(required=True)
    note = serializers.CharField(required=True, allow_null=True, allow_blank=True)
    invoice_sent = serializers.BooleanField(required=True, allow_null=True)

    class Meta:
        model = InvoiceMasterProctorShip
        fields = [
            "master_proctorship_id",
            "invoice_number",
            "fee_covered",
            "other_cost",
            "invoice_date",
            "note",
            "invoice_sent",
        ]

    def create(self, validated_data):
        try:
            with transaction.atomic():
                invoice = InvoiceMasterProctorShip.objects.create(**validated_data)
                invoice.save()
                return invoice
        except Exception as e:
            return None


class AttendanceFormMasterProctorShipSerailizers(serializers.ModelSerializer):
    master_proctorship_id = serializers.IntegerField(write_only=True)
    attendance_form = serializers.FileField(required=True)

    class Meta:
        model = AttendanceFormMasterProctorShip
        fields = ["id", "master_proctorship_id", "attendance_form"]

    def create(self, validated_data):
        try:
            with transaction.atomic():
                attendace_form = AttendanceFormMasterProctorShip.objects.create(
                    **validated_data
                )
                attendace_form.save()
                return attendace_form
        except Exception as e:
            return None


class MasterProctorshipStatusTestingSerializer(serializers.ModelSerializer):
    status = serializers.CharField(required=True)
    master_proctorship_activity_id = serializers.IntegerField(write_only=True)
    date = serializers.DateField(read_only=True)
    code = serializers.CharField(read_only=True)
    reason = serializers.CharField(required=False)

    class Meta:
        model = MasterProctorshipStatus
        fields = [
            "id",
            "status",
            "reason",
            "master_proctorship_activity_id",
            "code",
            "date",
        ]

    def create(self, validated_data):
        try:
            with transaction.atomic():
                status = validated_data.pop("status")
                validated_data["status"] = StatusConstantData.objects.get(code=status)
                status = MasterProctorshipStatus.objects.create(**validated_data)
                status.save()
                return status
        except Exception as e:
            return e


class AttendanceFormMasterProctorShipUpdateSerailizers(serializers.ModelSerializer):
    attendance_form = serializers.FileField(required=True)

    class Meta:
        model = AttendanceFormMasterProctorShip
        fields = ["id", "attendance_form"]

    def update(self, instance, validated_data):
        instance.attendance_form = validated_data.get(
            "attendance_form", instance.attendance_form
        )
        instance.save()
        return instance


class InvoiceMasterProctorShipUpdateSerializer(serializers.ModelSerializer):
    invoice_number = serializers.CharField(required=True)
    fee_covered = serializers.CharField(required=True)
    other_cost = serializers.CharField(required=True)
    invoice_date = serializers.DateField(required=True)
    note = serializers.CharField(required=True, allow_null=True, allow_blank=True)
    invoice_sent = serializers.BooleanField(required=True, allow_null=True)

    class Meta:
        model = InvoiceMasterProctorShip
        fields = [
            "invoice_number",
            "fee_covered",
            "other_cost",
            "invoice_date",
            "note",
            "invoice_sent",
        ]

    def update(self, instance, validated_data):
        try:
            instance.invoice_number = validated_data.get(
                "invoice_number", instance.invoice_number
            )
            instance.fee_covered = validated_data.get(
                "fee_covered", instance.fee_covered
            )
            instance.other_cost = validated_data.get("other_cost", instance.other_cost)
            instance.invoice_date = validated_data.get(
                "invoice_date", instance.invoice_date
            )
            instance.note = validated_data.get("note", instance.note)
            instance.invoice_sent = validated_data.get(
                "invoice_sent", instance.invoice_sent
            )
            instance.save()
            return instance
        except Exception as e:
            return e
