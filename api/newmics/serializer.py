import copy
from collections import OrderedDict

from django.db import transaction
from rest_framework import serializers

from api.feedback.models import Rating, Reason
from api.models import Hospital, HospitalCountires, Products
from api.newmics.models import (
    MicsAttendanceForm,
    MicsInvoice,
    MicsPercevalFeedback,
    MicsPreceptorship,
    MicsPreceptorshipProctors,
    MicsPreceptorshipProposal,
    MicsPreceptorshipStatus,
    MicsProctorship,
    MicsProctorshipCertificateForm,
    MicsProctorshipProctors,
    MicsProctorshipProposal,
    MicsProctorshipStatus,
    MicsTraineeFeedback,
    MicsTraineeProfile,
    NewMics,
)
from api.preceptorship.serializers import PreceptorshipProposalViewSerializer
from api.proctors.models import Proctors
from api.proctorship.models import ConstantData
from api.status.models import StatusConstantData
from api.users.models import User
from api.zone.models import Countries


class MicsPerceptorshipSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(write_only=True)
    hospital_id = serializers.IntegerField(write_only=True)
    note = serializers.CharField(required=True, allow_null=True, allow_blank=True)
    start_date = serializers.DateField(required=True)
    end_date = serializers.DateField(required=True)
    proctors_id = serializers.IntegerField(write_only=True)
    mics_id = serializers.IntegerField(read_only=True)

    class Meta:
        model = MicsPreceptorship
        fields = [
            "user_id",
            "hospital_id",
            "note",
            "start_date",
            "end_date",
            "proctors_id",
            "mics_id",
        ]

    def create(self, validated_data):
        try:
            with transaction.atomic():
                user_id = User.objects.get(validated_data.pop("user_id"))
                start_date = validated_data.pop("start_date")
                end_date = validated_data.pop("end_date")
                proctors_id = validated_data.pop("proctors_id")
                validated_data["user"] = user_id
                mics_perceptorship = MicsPreceptorship.objects.create(**validated_data)

                mics_perceptorship_status = MicsPreceptorshipStatus.objects.create(
                    user=user_id,
                    status=StatusConstantData.objects.get("pending"),
                    mics_preceptorship_activity=mics_perceptorship,
                )

                mics_purposal = MicsPreceptorshipProposal.objects.create(
                    start_date=start_date,
                    end_date=end_date,
                    status=mics_perceptorship_status,
                )
                mics_purposal_proctors = MicsPreceptorshipProctors.objects.create(
                    mics_preceptorship_proposal=mics_purposal,
                    proctors=Proctors.objects.get(id=proctors_id),
                )
                mics_perceptorship.save()
                return mics_perceptorship
        except Exception as e:
            return e


class MicsProctorshipSerializer(serializers.ModelSerializer):
    country_id = serializers.IntegerField(write_only=True)
    hospital_id = serializers.IntegerField(write_only=True)
    hotel = serializers.CharField(required=True)
    number_of_cases = serializers.IntegerField(required=True)
    transplant_time = serializers.CharField(required=True)
    start_date = serializers.DateField(write_only=True)
    end_date = serializers.DateField(write_only=True)
    is_second = serializers.BooleanField(write_only=True)

    class Meta:
        model = MicsProctorship
        fields = [
            "country_id",
            "is_second",
            "hospital_id",
            "hotel",
            "number_of_cases",
            "transplant_time",
            "start_date",
            "end_date",
        ]

    def create(self, validated_data):
        try:
            with transaction.atomic():

                start_date = validated_data.pop("start_date")
                end_date = validated_data.pop("end_date")
                mics_proctorship = MicsProctorship.objects.create(**validated_data)

                mics_proctorship_status = MicsProctorshipStatus.objects.create(
                    user=validated_data.get("user"),
                    status=StatusConstantData.objects.get(code="pending"),
                    proctorship_activity=mics_proctorship,
                )

                mics_purposal = MicsProctorshipProposal.objects.create(
                    start_date=start_date,
                    end_date=end_date,
                    status=mics_proctorship_status,
                )

                mics_purposal_proctors = MicsProctorshipProctors.objects.create(
                    porposal=mics_purposal,
                    proctors=validated_data.get("mics")
                    .mics_perceptotship.get()
                    .mics_preceptorshipStatus_status.all()[0]
                    .alter_mics_preceptorship_porposal.get()
                    .mics_preceptorship_porposal.get()
                    .proctors,
                )
                mics_proctorship.save()
                return mics_proctorship
        except Exception as e:
            return e


class MicsSerializer(serializers.ModelSerializer):
    is_rat = serializers.BooleanField(required=True)
    mics_perceptorship = serializers.DictField(
        required=True, allow_null=True, allow_empty=True
    )
    mics_proctorship = serializers.ListField(
        required=True, allow_null=True, allow_empty=True
    )
    trainee_profile = serializers.ListField(
        required=True, allow_null=True, allow_empty=True
    )

    class Meta:
        model = NewMics
        fields = ["is_rat", "mics_perceptorship", "trainee_profile", "mics_proctorship"]

    def create(self, validated_data):

        with transaction.atomic():

            mics_proctorship = validated_data.pop("mics_proctorship")
            mics_perceptorship = validated_data.pop("mics_perceptorship")
            trainee = validated_data.pop("trainee_profile")
            product = validated_data.pop("product")
            user = validated_data.get("user")
            # Create Mics
            new_mics = self.create_mics(user, is_rat=validated_data.get("is_rat"))
            # Create Perceptership
            mics_perceptorship_obj = self.create_mics_perceptership(
                user, product, new_mics, mics_perceptorship
            )
            # Create Perceptership Status
            mics_perceptorship_status = self.create_mics_perceptership_status(
                user, self.return_pending_status(), mics_perceptorship_obj
            )
            # Create Perceptership Proposal
            mics_purposal = self.create_mics_perceptership_proposal(
                mics_perceptorship_status,
                mics_perceptorship.get("start_date"),
                mics_perceptorship.get("end_date"),
            )
            # Create Perceptership Proctors
            proctors = self.return_proctor(mics_perceptorship.get("proctors_id"))
            mics_purposal_proctors = self.create_mics_perceptership_proctors(
                mics_purposal, proctors
            )

            # Create Mics 1st Proctorship
            if mics_proctorship:
                for each in mics_proctorship:
                    self.create_proctorship(user, new_mics, each, proctors)

            if trainee:
                for trainee_profile in trainee:
                    self.create_trainee(new_mics, trainee_profile)

            # new_mics.save()
            return new_mics

    def create_mics(self, user, is_rat):

        new_mics = NewMics.objects.create(user=user, is_rat=is_rat)
        return new_mics

    def create_mics_perceptership(self, user, product, new_mics, mics_perceptorship):

        mics_perceptorship = MicsPreceptorship.objects.create(
            user=user,
            product=product,
            hospital=mics_perceptorship.get("hospital"),
            mics=new_mics,
            note=mics_perceptorship.get("note"),
        )
        return mics_perceptorship

    def create_mics_perceptership_status(self, user, status, mics_perceptorship):

        mics_perceptorship_status = MicsPreceptorshipStatus.objects.create(
            user=user, status=status, mics_preceptorship_activity=mics_perceptorship
        )
        return mics_perceptorship_status

    def create_mics_perceptership_proposal(
        self, mics_perceptorship_status, start_date, end_date
    ):

        mics_purposal = MicsPreceptorshipProposal.objects.create(
            start_date=start_date, end_date=end_date, status=mics_perceptorship_status
        )
        return mics_purposal

    def create_mics_perceptership_proctors(self, mics_purposal, proctor):
        return MicsPreceptorshipProctors.objects.create(
            mics_preceptorship_proposal=mics_purposal, proctors=proctor
        )

    def return_pending_status(self):
        try:
            return StatusConstantData.objects.get(code="pending")
        except Exception as e:
            return None

    def return_proctor(self, id):
        return Proctors.objects.get(id=id)

    def create_proctorship(self, user, new_mics, each, proctor):
        mics_proctorships = MicsProctorship.objects.create(
            mics=new_mics,
            user=user,
            country=self.return_country(each.pop("country_id")),
            hospital=self.return_hospital(each.pop("hospital_id")),
            hotel=each.pop("hotel"),
            number_of_cases=each.pop("number_of_cases"),
            transplant_time=each.pop("transplant_time"),
            is_second=each.pop("is_second"),
        )
        mics_proctorship_status = MicsProctorshipStatus.objects.create(
            user=user,
            status=self.return_pending_status(),
            proctorship_activity=mics_proctorships,
        )
        mics_proctorship_purposal = MicsProctorshipProposal.objects.create(
            status=mics_proctorship_status,
            start_date=each.pop("start_date"),
            end_date=each.pop("end_date"),
        )

        MicsProctorshipProctors.objects.create(
            porposal=mics_proctorship_purposal, proctors=proctor
        )
        return mics_proctorships

    def create_trainee(self, new_mics, trainee_profile):
        return MicsTraineeProfile.objects.create(
            mics=new_mics,
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
            corcym_accompanying_rep=trainee_profile["corcym_accompanying_rep"],
            country=self.return_country(trainee_profile["country_id"]),
            hospital=self.return_hospital(trainee_profile["hospital_id"]),
            interest_invasive=trainee_profile["interest_invasive"],
            status=True,
        )

    def return_hospital(self, id):
        return Hospital.objects.get(id=int(id))

    def return_country(self, id):
        return Countries.objects.get(id=int(id))


# View Serializers
class MicsProctorshipPurposalSerializer(serializers.ModelSerializer):
    note = serializers.CharField(read_only=True)
    start_date = serializers.DateField(read_only=True)
    end_date = serializers.DateField(read_only=True)
    proctors = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = MicsProctorshipProctors
        fields = ["start_date", "end_date", "note", "proctors"]

    def get_proctors(self, obj):
        try:
            return obj.mics_proctor_porposal.get().proctors.user.name
        except:
            return None


class MicsProctorShortshipStatusSerializer(serializers.ModelSerializer):
    status = serializers.CharField(read_only=True)
    code = serializers.SerializerMethodField()
    date = serializers.DateField(read_only=True)
    reason = serializers.CharField(read_only=True)
    user = serializers.SerializerMethodField()
    alternatives = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = MicsProctorshipStatus
        fields = ["status", "date", "user", "reason", "code", "alternatives"]

    def get_user(self, obj):
        try:
            return obj.user.name
        except:
            return None

    def get_alternatives(self, obj):
        try:
            return MicsProctorshipPurposalSerializer(
                MicsProctorshipProposal.objects.get(status__id=obj.id)
            ).data
        except:
            return None

    def get_code(self, obj):
        try:
            return obj.status.code
        except Exception as e:
            return None


class ProctorshipViewSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    country = serializers.SerializerMethodField(read_only=True)
    hospital = serializers.SerializerMethodField(read_only=True)
    note = serializers.CharField(read_only=True)
    hotel = serializers.CharField(read_only=True)
    number_of_cases = serializers.IntegerField(read_only=True)
    transplant_time = serializers.CharField(read_only=True)
    is_second = serializers.BooleanField(read_only=True)
    mics_proctorship_status = serializers.SerializerMethodField(read_only=True)
    perceval = serializers.SerializerMethodField(read_only=True)
    attendant_form = serializers.SerializerMethodField(read_only=True)
    invoice = serializers.SerializerMethodField(read_only=True)
    certificate = serializers.SerializerMethodField(read_only=True)
    trainee_data = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = MicsProctorship
        fields = [
            "id",
            "country",
            "hospital",
            "note",
            "perceval",
            "attendant_form",
            "certificate",
            "invoice",
            "mics_proctorship_status",
            "hotel",
            "transplant_time",
            "is_second",
            "number_of_cases",
            "trainee_data",
        ]

    def get_certificate(self, obj):
        try:
            return MicsCertificateFormSerailizers(
                obj.mics_certificate_form_mics_proctorship.get()
            ).data
        except Exception as e:
            return None

    def get_perceval(self, obj):
        try:
            return MicsPercevalSerializer(
                obj.mics_perceval_feedback_mics_proctorship.get()
            ).data
        except Exception as e:
            return None

    def get_attendant_form(self, obj):
        try:
            return MicsAttendanceFormSerailizers(
                obj.mics_attendance_form_mics_proctorship.get()
            ).data
        except Exception as e:
            return None

    def get_invoice(self, obj):
        try:
            return MicsInvoiceSerializer(obj.mics_invoice_mics_proctorship.get()).data
        except Exception as e:
            return None

    def get_trainee_data(self, obj):
        try:
            return MicsTraineeFeedbackSerializer(
                obj.mics_trainee_feedback_mics_proctorship.all(), many=True
            ).data
        except Exception as e:
            return None

    def get_country(self, obj):
        try:
            return obj.country.name
        except:
            return None

    def get_hospital(self, obj):
        try:
            return obj.hospital.hospital_name
        except:
            return None

    def get_mics_proctorship_status(self, obj):
        try:
            return MicsProctorShortshipStatusSerializer(
                MicsProctorshipStatus.objects.filter(proctorship_activity__id=obj.id),
                many=True,
            ).data
        except:
            return None


class MicsPerceptorshipPurposalSerializer(serializers.ModelSerializer):
    note = serializers.CharField(read_only=True)
    start_date = serializers.DateField(read_only=True)
    end_date = serializers.DateField(read_only=True)
    proctors = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = MicsPreceptorshipProposal
        fields = ["start_date", "end_date", "note", "proctors"]

    def get_proctors(self, obj):
        try:
            return obj.mics_preceptorship_porposal.get().proctors.user.name
        except:
            return None


class MicsPerceptorshipStatusSerializer(serializers.ModelSerializer):
    status = serializers.CharField(read_only=True)
    code = serializers.SerializerMethodField(read_only=True)
    date = serializers.DateField(read_only=True)
    user = serializers.SerializerMethodField()
    reason = serializers.CharField(read_only=True)
    alternatives = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = MicsPreceptorshipStatus
        fields = ["status", "date", "user", "reason", "code", "alternatives"]

    def get_user(self, obj):
        try:
            return obj.user.name
        except:
            return None

    def get_alternatives(self, obj):
        try:
            return MicsPerceptorshipPurposalSerializer(
                MicsPreceptorshipProposal.objects.get(status__id=obj.id)
            ).data
        except:
            return None

    def get_code(self, obj):
        try:
            return obj.status.code
        except Exception as e:
            return None


class PerceptorshipViewSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    product_id = serializers.SerializerMethodField(read_only=True)
    product = serializers.SerializerMethodField(read_only=True)
    hospital = serializers.SerializerMethodField(read_only=True)
    note = serializers.CharField(read_only=True)
    mics_perceptorship_status = serializers.SerializerMethodField(read_only=True)
    invoice = serializers.SerializerMethodField(read_only=True)
    trainee_data = serializers.SerializerMethodField(read_only=True)
    attendant_form = serializers.SerializerMethodField(read_only=True)
    trainees = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = MicsPreceptorship
        fields = [
            "id",
            "product_id",
            "product",
            "hospital",
            "trainees",
            "note",
            "invoice",
            "trainee_data",
            "attendant_form",
            "mics_perceptorship_status",
        ]

    def get_attendant_form(self, obj):
        try:
            return MicsAttendanceFormSerailizers(
                obj.mics_attendance_form_mics_perceptership.get()
            ).data
        except Exception as e:
            return None

    def get_invoice(self, obj):
        try:
            return MicsInvoiceSerializer(obj.mics_invoice_mics_perceptership.get()).data
        except Exception as e:
            return None

    def get_trainee_data(self, obj):
        try:
            return MicsTraineeFeedbackSerializer(
                obj.mics_trainee_feedback_mics_perceptership.all(), many=True
            ).data
        except Exception as e:
            return None

    def get_trainees(self, obj):
        return obj.hospital.number_of_trainee

    def get_product(self, obj):
        try:
            return obj.product.product_name
        except:
            return None

    def get_product_id(self, obj):
        try:
            return obj.product.id
        except:
            return None

    def get_hospital(self, obj):
        try:
            return obj.hospital.hospital_name
        except:
            return None

    def get_mics_perceptorship_status(self, obj):
        try:
            return MicsPerceptorshipStatusSerializer(
                MicsPreceptorshipStatus.objects.filter(
                    mics_preceptorship_activity__id=obj.id
                ),
                many=True,
            ).data
        except Exception as e:
            return None


class TraineeMicsViewSerializer(serializers.ModelSerializer):
    title = serializers.CharField(read_only=True)
    name = serializers.CharField(read_only=True)
    surname = serializers.CharField(read_only=True)
    corcym_accompanying_rep = serializers.CharField(read_only=True)
    current_preferential = serializers.CharField(read_only=True)
    mvr_case_per_year = serializers.IntegerField(read_only=True)
    mvr_case_per_year_by_trainee = serializers.IntegerField(read_only=True)
    note = serializers.CharField(read_only=True, allow_null=True, allow_blank=True)
    hospital = serializers.SerializerMethodField(read_only=True)
    country = serializers.SerializerMethodField(read_only=True)
    status = serializers.BooleanField(read_only=True)
    revoke = serializers.BooleanField(read_only=True)
    interest_invasive = serializers.BooleanField(read_only=True)

    class Meta:
        model = MicsTraineeProfile
        fields = [
            "id",
            "hospital",
            "country",
            "title",
            "status",
            "revoke",
            "name",
            "surname",
            "corcym_accompanying_rep",
            "current_preferential",
            "mvr_case_per_year",
            "mvr_case_per_year_by_trainee",
            "note",
            "interest_invasive",
        ]

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


class MicsViewSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField(read_only=True)
    is_rat = serializers.BooleanField(read_only=True)
    mics_perceptorship = serializers.SerializerMethodField(read_only=True)
    mics_proctorship = serializers.SerializerMethodField(read_only=True)
    trainee = serializers.SerializerMethodField(read_only=True)
    mics_second_proctorship = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = NewMics
        fields = [
            "id",
            "user",
            "is_rat",
            "mics_perceptorship",
            "mics_proctorship",
            "trainee",
            "mics_second_proctorship",
        ]

    def get_user(self, obj):
        try:
            return obj.user.name
        except:
            return None

    def get_mics_perceptorship(self, obj):
        try:
            return PerceptorshipViewSerializer(
                MicsPreceptorship.objects.get(mics__id=obj.id)
            ).data
        except:
            return None

    def get_mics_proctorship(self, obj):
        try:
            return ProctorshipViewSerializer(
                MicsProctorship.objects.get(
                    mics__id=obj.id, is_second=False, is_active=True
                )
            ).data
        except:
            return None

    def get_mics_second_proctorship(self, obj):
        try:
            return ProctorshipViewSerializer(
                MicsProctorship.objects.get(
                    mics__id=obj.id, is_second=True, is_active=True
                )
            ).data
        except:
            return None

    def get_trainee(self, obj):
        try:
            return TraineeMicsViewSerializer(
                MicsTraineeProfile.objects.filter(mics__id=obj.id), many=True
            ).data
        except:
            return None


class MicsTraineeProfileSerializer(serializers.ModelSerializer):
    title = serializers.CharField(required=True)
    name = serializers.CharField(required=True)
    surname = serializers.CharField(required=True)
    corcym_accompanying_rep = serializers.CharField(required=True)
    current_preferential = serializers.CharField(required=True)
    mvr_case_per_year = serializers.IntegerField(required=True)
    mvr_case_per_year_by_trainee = serializers.IntegerField(required=True)
    note = serializers.CharField(required=True, allow_blank=True, allow_null=True)
    hospital = serializers.SerializerMethodField(read_only=True)
    hospital_id = serializers.IntegerField(write_only=True)
    country = serializers.SerializerMethodField(read_only=True)
    country_id = serializers.IntegerField(write_only=True)
    status = serializers.BooleanField(read_only=True)
    interest_invasive = serializers.BooleanField(required=True)

    class Meta:
        model = MicsTraineeProfile
        fields = [
            "id",
            "status",
            "interest_invasive",
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

        with transaction.atomic():
            title = validated_data.pop("title")
            current_preferential = validated_data.pop("current_preferential")
            validated_data["mics"] = self.context.get("mics")
            trainee = MicsTraineeProfile.objects.create(**validated_data)
            trainee.title = ConstantData.objects.get(code=title)
            trainee.current_preferential = ConstantData.objects.get(
                code=current_preferential
            )
            trainee.save()
            return trainee

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

    def get_hospital(self, obj):
        try:
            return obj.hospital.name
        except:
            return None

    def get_country(self, obj):
        try:
            return obj.country.name
        except:
            return None

    def get_proctorship(self, obj):
        try:
            return obj.proctorship.id
        except:
            return None

    def get_preceptorship(self, obj):
        try:
            return obj.preceptorship.id
        except:
            return None

    def get_master_proctorship(self, obj):
        try:
            return obj.master_proctorship.id
        except:
            return None


class MultipleMicsTraineeProfileSerializer(serializers.ModelSerializer):
    title = serializers.CharField(required=True)
    name = serializers.CharField(required=True)
    surname = serializers.CharField(required=True)
    corcym_accompanying_rep = serializers.CharField(required=True)
    current_preferential = serializers.CharField(required=True)
    mvr_case_per_year = serializers.IntegerField(required=True)
    mvr_case_per_year_by_trainee = serializers.IntegerField(required=True)
    note = serializers.CharField(required=True, allow_blank=True, allow_null=True)
    hospital = serializers.SerializerMethodField(read_only=True)
    hospital_id = serializers.IntegerField(write_only=True)
    country = serializers.SerializerMethodField(read_only=True)
    country_id = serializers.IntegerField(write_only=True)
    status = serializers.BooleanField(read_only=True)
    interest_invasive = serializers.BooleanField(required=True)

    class Meta:
        model = MicsTraineeProfile
        fields = [
            "id",
            "status",
            "interest_invasive",
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
                trainee = MicsTraineeProfile.objects.create(**validated_data)
                trainee.title = ConstantData.objects.get(code=title)
                trainee.current_preferential = ConstantData.objects.get(
                    code=current_preferential
                )
                trainee.save()
                return trainee
        except Exception as e:
            return e

    def get_hospital(self, obj):
        try:
            return obj.hospital.name
        except:
            return None

    def get_country(self, obj):
        try:
            return obj.country.name
        except:
            return None

    def get_proctorship(self, obj):
        try:
            return obj.proctorship.id
        except:
            return None

    def get_preceptorship(self, obj):
        try:
            return obj.preceptorship.id
        except:
            return None

    def get_master_proctorship(self, obj):
        try:
            return obj.master_proctorship.id
        except:
            return None


class MicsProctorshipStatusSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField(read_only=True)
    status = serializers.CharField(required=True)
    user_id = serializers.IntegerField(write_only=True)
    proctorship_activity_id = serializers.IntegerField(write_only=True)
    date = serializers.DateField(read_only=True)
    purposal = serializers.SerializerMethodField(read_only=True)
    alternatives_data = serializers.DictField(required=False)
    code = serializers.CharField(read_only=True)
    reason = serializers.CharField(required=False)

    class Meta:
        model = MicsProctorshipStatus
        fields = [
            "id",
            "user",
            "status",
            "user_id",
            "reason",
            "proctorship_activity_id",
            "code",
            "date",
            "purposal",
            "alternatives_data",
        ]

    def create(self, validated_data):
        try:
            with transaction.atomic():
                if "alternatives_data" in validated_data.keys():
                    alternatives_data = validated_data.pop("alternatives_data")

                proctorship_activity_id = validated_data.pop("proctorship_activity_id")
                validated_data["proctorship_activity_id"] = proctorship_activity_id
                MicsProctorshipStatus.objects.filter(
                    proctorship_activity__id=proctorship_activity_id
                ).update(is_active=False)
                status = validated_data.pop("status")
                user_id = validated_data.pop("user_id")
                validated_data["user_id"] = user_id
                validated_data["status"] = StatusConstantData.objects.get(code=status)
                status = MicsProctorshipStatus.objects.create(**validated_data)

                if len(alternatives_data) != 0:
                    data_add = {
                        "status": status,
                        "note": alternatives_data["note"],
                        "start_date": alternatives_data["start_date"],
                        "end_date": alternatives_data["end_date"],
                    }
                    alt = MicsProctorshipProposal.objects.create(**data_add)
                    if "proctor_user_id" in alternatives_data.keys():
                        qs = MicsProctorshipProctors.objects.filter(
                            porposal__status__proctorship_activity__id=proctorship_activity_id,
                            status=True,
                        )
                        qs.update(status=False)
                        proctors = {
                            "porposal": alt,
                            "proctors": Proctors.objects.get(
                                id=alternatives_data["proctor_user_id"]
                            ),
                            "proctor_order": 1,
                        }
                        MicsProctorshipProctors.objects.create(**proctors)

                status.save()
                return status
        except Exception as e:
            return e

    def get_user(self, obj):
        try:
            return obj.user.name
        except:
            return None

    def get_purposal(self, obj):
        try:
            return MicsProctorshipPurposalSerializer(
                obj.alter_proctorship_porposal.get()
            ).data
        except:
            return None


class MicsPreceptorshipStatusSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField(read_only=True)
    status = serializers.CharField(required=True)
    user_id = serializers.IntegerField(write_only=True)
    mics_preceptorship_activity_id = serializers.IntegerField(write_only=True)
    date = serializers.DateField(read_only=True)
    purposal = serializers.SerializerMethodField(read_only=True)
    alternatives_data = serializers.DictField(required=False)
    code = serializers.CharField(read_only=True)
    reason = serializers.CharField(required=False)

    class Meta:
        model = MicsPreceptorshipStatus
        fields = [
            "id",
            "user",
            "status",
            "user_id",
            "reason",
            "mics_preceptorship_activity_id",
            "code",
            "date",
            "purposal",
            "alternatives_data",
        ]

    def create(self, validated_data):
        try:
            with transaction.atomic():
                alternatives_data = OrderedDict()
                if "alternatives_data" in validated_data.keys():
                    alternatives_data = validated_data.pop("alternatives_data")

                mics_preceptorship_activity_id = validated_data.pop(
                    "mics_preceptorship_activity_id"
                )
                validated_data[
                    "mics_preceptorship_activity_id"
                ] = mics_preceptorship_activity_id

                MicsPreceptorshipStatus.objects.filter(
                    mics_preceptorship_activity__id=mics_preceptorship_activity_id
                ).update(is_active=False)
                status = validated_data.pop("status")
                user_id = validated_data.pop("user_id")
                validated_data["user_id"] = user_id
                validated_data["status"] = StatusConstantData.objects.get(code=status)
                status = MicsPreceptorshipStatus.objects.create(**validated_data)

                if len(alternatives_data) != 0:
                    data_add = {
                        "status": status,
                        "note": alternatives_data["note"],
                        "start_date": alternatives_data["start_date"],
                        "end_date": alternatives_data["end_date"],
                    }
                    alt = MicsPreceptorshipProposal.objects.create(**data_add)
                    if "proctor_user_id" in alternatives_data.keys():
                        qs = MicsPreceptorshipProctors.objects.filter(
                            mics_preceptorship_proposal__status__mics_preceptorship_activity__id=mics_preceptorship_activity_id,
                            status=True,
                        )
                        if qs:
                            qs.update(status=False)
                        proctors = {
                            "mics_preceptorship_proposal": alt,
                            "proctors": Proctors.objects.get(
                                id=alternatives_data["proctor_user_id"]
                            ),
                        }
                        alpha = MicsPreceptorshipProctors.objects.create(**proctors)

                status.save()
                return status
        except Exception as e:
            return e

    def get_user(self, obj):
        try:
            return obj.user.name
        except:
            return None

    def get_purposal(self, obj):
        try:
            return MicsPerceptorshipPurposalSerializer(
                obj.alter_proctorship_porposal.get()
            ).data
        except:
            return None


class PerceptorshipListingViewSerializer(serializers.ModelSerializer):
    product = serializers.SerializerMethodField(read_only=True)
    hospital = serializers.SerializerMethodField(read_only=True)
    note = serializers.CharField(read_only=True)
    mics_perceptorship_status = serializers.SerializerMethodField(read_only=True)
    mics_perceptorship_purposal = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = MicsPreceptorship
        fields = [
            "product",
            "hospital",
            "note",
            "mics_perceptorship_status",
            "mics_perceptorship_purposal",
        ]

    def get_product(self, obj):
        try:
            return obj.product.product_name
        except:
            return None

    def get_hospital(self, obj):
        try:
            return obj.hospital.hospital_name
        except:
            return None

    def get_mics_perceptorship_status(self, obj):
        try:
            return MicsPerceptorshipStatusSerializer(
                MicsPreceptorshipStatus.objects.filter(
                    mics_preceptorship_activity__id=obj.id
                ).latest("timestamp")
            ).data["status"]
        except:
            return None

    def get_mics_perceptorship_purposal(self, obj):
        try:
            return MicsPerceptorshipPurposalSerializer(
                obj.mics_preceptorshipStatus_status.all()
                .latest("timestamp")
                .alter_mics_preceptorship_porposal.all()
                .latest("created_on")
            ).data
        except:
            return None


class ProctorshipListingViewSerializer(serializers.ModelSerializer):
    country = serializers.SerializerMethodField(read_only=True)
    hospital = serializers.SerializerMethodField(read_only=True)
    note = serializers.CharField(read_only=True)
    hotel = serializers.CharField(read_only=True)
    number_of_cases = serializers.IntegerField(read_only=True)
    transplant_time = serializers.CharField(read_only=True)
    is_second = serializers.BooleanField(read_only=True)
    mics_proctorship_status = serializers.SerializerMethodField(read_only=True)
    mics_proctorship_purposal = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = MicsProctorship
        fields = [
            "country",
            "hospital",
            "note",
            "mics_proctorship_status",
            "hotel",
            "transplant_time",
            "is_second",
            "number_of_cases",
            "mics_proctorship_purposal",
        ]

    def get_country(self, obj):
        try:
            return obj.country.name
        except:
            return None

    def get_hospital(self, obj):
        try:
            return obj.hospital.hospital_name
        except:
            return None

    def get_mics_proctorship_status(self, obj):
        try:
            return MicsProctorShortshipStatusSerializer(
                MicsProctorshipStatus.objects.filter(
                    proctorship_activity__id=obj.id
                ).latest("timestamp")
            ).data["status"]
        except:
            return None

    def get_mics_proctorship_purposal(self, obj):
        try:
            return MicsProctorshipPurposalSerializer(
                obj.mics_proctorship_status.all()
                .latest("timestamp")
                .mics_proctorship_porposal.all()
                .latest("created_on")
            ).data
        except:
            return None


class MicsViewListingSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField(read_only=True)
    is_rat = serializers.BooleanField(read_only=True)
    mics_perceptorship = serializers.SerializerMethodField(read_only=True)
    mics_proctorship = serializers.SerializerMethodField(read_only=True)
    mics_second_proctorship = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = NewMics
        fields = [
            "id",
            "user",
            "is_rat",
            "mics_perceptorship",
            "mics_proctorship",
            "mics_second_proctorship",
        ]

    def get_user(self, obj):
        try:
            return obj.user.name
        except:
            return None

    def get_mics_perceptorship(self, obj):
        try:
            return PerceptorshipListingViewSerializer(
                MicsPreceptorship.objects.get(mics__id=obj.id)
            ).data
        except:
            return None

    def get_mics_proctorship(self, obj):
        try:
            return ProctorshipListingViewSerializer(
                MicsProctorship.objects.get(mics__id=obj.id, is_second=False)
            ).data
        except:
            return None

    def get_mics_second_proctorship(self, obj):
        try:
            return ProctorshipListingViewSerializer(
                MicsProctorship.objects.get(mics__id=obj.id, is_second=True)
            ).data
        except:
            return None


class RecentPreceptorshipViewSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField()
    user = serializers.SerializerMethodField(read_only=True)
    product = serializers.SerializerMethodField(read_only=True)
    hospital = serializers.SerializerMethodField(read_only=True)
    note = serializers.CharField(read_only=True)
    training_type = serializers.CharField(read_only=True)
    types_of_first_training = serializers.CharField(read_only=True)
    type_advance_training = serializers.CharField(read_only=True)
    specific_training = serializers.CharField(read_only=True)
    not_implant_regularly = serializers.CharField(read_only=True)
    status = serializers.SerializerMethodField(read_only=True)
    rem_seats = serializers.SerializerMethodField(read_only=True)
    proctor = serializers.SerializerMethodField(read_only=True)
    start_date = serializers.SerializerMethodField(read_only=True)
    activity_id = serializers.CharField(read_only=True)

    class Meta:
        model = MicsPreceptorship
        fields = [
            "id",
            "user",
            "product",
            "proctor",
            "start_date",
            "hospital",
            "note",
            "training_type",
            "types_of_first_training",
            "type_advance_training",
            "specific_training",
            "status",
            "not_implant_regularly",
            "rem_seats",
            "activity_id",
        ]

    def get_id(self, obj):
        try:
            return obj.mics_id
        except:
            return None

    def get_proctor(self, obj):
        try:
            return (
                obj.mics_preceptorshipStatus_status.filter(is_active=True)[0]
                .alter_mics_preceptorship_porposal.get()
                .mics_preceptorship_porposal.get()
                .proctors.user.name
            )
        except:
            return None

    def get_start_date(self, obj):
        try:
            return (
                obj.mics_preceptorshipStatus_status.filter(is_active=True)[0]
                .alter_mics_preceptorship_porposal.get()
                .start_date
            )
        except:
            return None

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
            return obj.hospital.hospital_name
        except:
            return None

    def get_hospital_id(self, obj):
        try:
            return obj.hospital.id
        except:
            return None

    def get_secondary_product(self, obj):
        try:
            return obj.secondary_product.product_name
        except:
            return None

    def get_secondary_product_id(self, obj):
        try:
            return obj.secondary_product.id
        except:
            return None

    def get_product(self, obj):
        try:
            return obj.product.product_name
        except:
            return None

    def get_product_id(self, obj):
        try:
            return obj.product.id
        except:
            return None

    def get_status(self, obj):
        try:
            return obj.mics_preceptorshipStatus_status.filter(is_active=True)[
                0
            ].status.name
        except:
            return None

    def get_rem_seats(self, obj):
        try:
            hospital = obj.hospital.number_of_trainee
            traine = obj.mics.mics_traineeprofile.filter(revoke=False)
            rem = hospital - traine.count()
            if rem > 0:
                return rem
            else:
                return 0
        except Exception as e:
            return None


class HospitalForMICSSerializer(serializers.ModelSerializer):
    hospital_name = serializers.CharField(read_only=True)
    number_of_trainee = serializers.IntegerField(read_only=True)

    class Meta:
        model = Hospital
        fields = ["id", "hospital_name", "number_of_trainee"]


class CEOProctorsZoneViewSerializer(serializers.ModelSerializer):
    proctor_name = serializers.SerializerMethodField(read_only=True)
    proctor_id = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Proctors
        fields = ["proctor_name", "proctor_id"]

    def get_proctor_name(self, obj):
        try:
            return obj.user.name
        except:
            return None

    def get_proctor_id(self, obj):
        try:
            return obj.id
        except:
            return None


class MicsPerceptorshipValidateStatusSerializer(serializers.ModelSerializer):
    start_date = serializers.DateField(required=True)
    end_date = serializers.DateField(required=True)
    note = serializers.CharField(required=True, allow_null=True, allow_blank=True)
    proctors = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = MicsPreceptorshipProposal
        fields = ["id", "note", "end_date", "start_date", "proctors"]

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

    def get_proctors(self, obj):
        try:
            return PreceptorshipProctorsSerializer(
                obj.proctor_porposal.proctors, many=True
            ).data
        except:
            return None


class UpdateStatusPerceptershipSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField(read_only=True)
    status = serializers.CharField(required=True)

    date = serializers.DateField(read_only=True)
    purposal = serializers.SerializerMethodField(read_only=True)
    alternatives_data = MicsPerceptorshipValidateStatusSerializer(required=False)
    code = serializers.CharField(read_only=True)
    reason = serializers.CharField(required=False, allow_null=True, allow_blank=True)

    class Meta:
        model = MicsPreceptorshipStatus
        fields = [
            "id",
            "user",
            "status",
            "reason",
            "code",
            "date",
            "purposal",
            "alternatives_data",
        ]

    def create(self, validated_data):

        with transaction.atomic():
            alternatives_data = OrderedDict()
            if "alternatives_data" in validated_data.keys():
                alternatives_data = validated_data.pop("alternatives_data")
            mics = self.context.get("mics")
            new_ob = copy.copy(validated_data)

            validated_data[
                "mics_preceptorship_activity"
            ] = mics.mics_perceptotship.get()

            MicsPreceptorshipStatus.objects.filter(
                mics_preceptorship_activity__mics__id=mics.id
            ).update(is_active=False)
            status = validated_data.pop("status")

            validated_data["status"] = StatusConstantData.objects.get(code=status)
            status = MicsPreceptorshipStatus.objects.create(**validated_data)

            if len(alternatives_data) != 0:
                data_add = {
                    "status": status,
                    "note": alternatives_data["note"],
                    "start_date": alternatives_data["start_date"],
                    "end_date": alternatives_data["end_date"],
                }
                alt = MicsPreceptorshipProposal.objects.create(**data_add)
                qs = MicsPreceptorshipProctors.objects.get(
                    mics_preceptorship_proposal__status__mics_preceptorship_activity__mics__id=mics.id,
                    status=True,
                )
                if qs:
                    qs.status = False
                    qs.save()
                proctors = {
                    "mics_preceptorship_proposal": alt,
                    "proctors": qs.proctors,
                }
                alpha = MicsPreceptorshipProctors.objects.create(**proctors)

            if new_ob["status"] == "cancelled":
                for obj in mics.mics_peroctorship.filter(is_active=True):
                    new_ob["proctorship_activity"] = obj
                    obj.is_active = False
                    obj.save()
                    MicsProctorshipStatus.objects.filter(
                        proctorship_activity__mics__id=mics.id
                    ).update(is_active=False)
                    status = new_ob.pop("status")

                    new_ob["status"] = StatusConstantData.objects.get(code=status)
                    status = MicsProctorshipStatus.objects.create(**new_ob)

            status.save()
            return status

    def get_user(self, obj):
        try:
            return obj.user.name
        except:
            return None

    def get_purposal(self, obj):
        try:
            return PreceptorshipProposalViewSerializer(
                obj.alter_proctorship_porposal.get()
            ).data
        except:
            return None


class MicsProctorshipValidateStatusSerializer(serializers.ModelSerializer):
    start_date = serializers.DateField(required=True)
    end_date = serializers.DateField(required=True)
    note = serializers.CharField(required=True, allow_null=True, allow_blank=True)
    proctors = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = MicsPreceptorshipProposal
        fields = ["id", "note", "end_date", "start_date", "proctors"]

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

    def get_proctors(self, obj):
        try:
            return PreceptorshipProctorsSerializer(
                obj.proctor_porposal.proctors, many=True
            ).data
        except:
            return None


class UpdateStatusProctorshipSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField(read_only=True)
    status = serializers.CharField(required=True)

    date = serializers.DateField(read_only=True)
    purposal = serializers.SerializerMethodField(read_only=True)
    alternatives_data = MicsProctorshipValidateStatusSerializer(required=False)
    code = serializers.CharField(read_only=True)
    reason = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    is_second = serializers.BooleanField(default=False)

    class Meta:
        model = MicsProctorshipStatus
        fields = [
            "id",
            "user",
            "status",
            "reason",
            "code",
            "date",
            "purposal",
            "alternatives_data",
            "is_second",
        ]

    def create(self, validated_data):

        with transaction.atomic():
            alternatives_data = OrderedDict()
            if "alternatives_data" in validated_data.keys():
                alternatives_data = validated_data.pop("alternatives_data")
            mics = self.context.get("mics")
            new_obj = copy.copy(validated_data)
            is_second = validated_data.pop("is_second")
            validated_data["proctorship_activity"] = mics.mics_peroctorship.get(
                is_active=True, is_second=is_second
            )

            MicsProctorshipStatus.objects.filter(
                proctorship_activity__mics__id=mics.id,
                proctorship_activity__is_second=is_second,
            ).update(is_active=False)
            if new_obj["status"] == "cancelled":
                MicsProctorship.objects.filter(
                    mics__id=mics.id, is_second=is_second
                ).update(is_active=False)
            status = validated_data.pop("status")

            validated_data["status"] = StatusConstantData.objects.get(code=status)
            status = MicsProctorshipStatus.objects.create(**validated_data)

            if len(alternatives_data) != 0:
                data_add = {
                    "status": status,
                    "note": alternatives_data["note"],
                    "start_date": alternatives_data["start_date"],
                    "end_date": alternatives_data["end_date"],
                }
                alt = MicsProctorshipProposal.objects.create(**data_add)
                qs = MicsProctorshipProctors.objects.get(
                    porposal__status__proctorship_activity__is_active=True,
                    porposal__status__proctorship_activity__is_second=is_second,
                    porposal__status__proctorship_activity__mics__id=mics.id,
                    status=True,
                )
                if qs:
                    qs.status = False
                    qs.save()
                proctors = {
                    "porposal": alt,
                    "proctors": qs.proctors,
                }
                alpha = MicsProctorshipProctors.objects.create(**proctors)

            try:
                if new_obj["status"] == "cancelled" and not is_second:
                    validated_data["proctorship_activity"] = mics.mics_peroctorship.get(
                        is_active=True, is_second=True
                    )

                    MicsProctorshipStatus.objects.filter(
                        proctorship_activity__mics__id=mics.id,
                        proctorship_activity__is_second=True,
                    ).update(is_active=False)
                    MicsProctorship.objects.filter(
                        mics__id=mics.id, is_second=True
                    ).update(is_active=False)
                    status = validated_data.pop("status")

                    validated_data["status"] = StatusConstantData.objects.get(
                        code=status
                    )
                    status = MicsProctorshipStatus.objects.create(**validated_data)

            except Exception as e:
                pass
            status.save()
            return status

    def get_user(self, obj):
        try:
            return obj.user.name
        except:
            return None

    def get_purposal(self, obj):
        try:
            return PreceptorshipProposalViewSerializer(
                obj.alter_proctorship_porposal.get()
            ).data
        except:
            return None


class MICSHospitalSerializer(serializers.ModelSerializer):
    hospital_name = serializers.CharField(required=True)
    number_of_trainee = serializers.IntegerField(required=True)
    products = serializers.StringRelatedField(many=True, read_only=True)
    country = serializers.SerializerMethodField(read_only=True)
    location = serializers.CharField(required=True)
    is_it_preceptorship = serializers.BooleanField(required=True)
    qualified_for_news_mics_program = serializers.BooleanField(required=True)
    cognos_id = serializers.CharField(required=True)
    country_id = serializers.IntegerField(write_only=True)
    products_id = serializers.ListField(write_only=True)

    class Meta:
        model = Hospital
        fields = (
            "id",
            "hospital_name",
            "number_of_trainee",
            "products_id",
            "products",
            "country",
            "country_id",
            "location",
            "is_it_preceptorship",
            "qualified_for_news_mics_program",
            "cognos_id",
        )

    def create(self, validated_data):
        try:
            with transaction.atomic():
                x = validated_data.pop("products_id")
                country_id = validated_data.pop("country_id")
                hospital = Hospital.objects.create(**validated_data)
                hospital_countries = HospitalCountires.objects.create(
                    country=Countries.objects.get(id=country_id), hospital=hospital
                )
                for product in x:
                    product_obj = Products.objects.get(id=product)
                    hospital.products.add(product_obj)

                hospital.save()
                return hospital
        except Exception as e:
            return e

    def get_country(self, obj):
        try:
            return obj.hospital_id.get().country.name
        except:
            return ""

    def get_products(self, obj):
        try:
            return obj.products.product_name
        except:
            return ""


class MicsPercevalSerializer(serializers.ModelSerializer):
    proctorship = serializers.SerializerMethodField(read_only=True)
    num_of_patients = serializers.IntegerField(required=True)
    is_advance = serializers.BooleanField(required=True)
    implanted_patient = serializers.IntegerField(required=True)
    implanted_perceval = serializers.IntegerField(required=True)
    reason_low_num_patients = serializers.SerializerMethodField(read_only=True)
    rate_of_experince = serializers.SerializerMethodField(read_only=True)
    is_trainee_implant = serializers.BooleanField(required=True)
    any_leason = serializers.CharField(required=True)
    report = serializers.FileField(required=True)
    reason_low_num_patients_code = serializers.CharField(write_only=True)
    rate_of_experince_code = serializers.CharField(write_only=True)

    class Meta:
        model = MicsPercevalFeedback
        fields = (
            "id",
            "proctorship",
            "num_of_patients",
            "is_advance",
            "implanted_patient",
            "implanted_perceval",
            "reason_low_num_patients",
            "rate_of_experince",
            "is_trainee_implant",
            "any_leason",
            "report",
            "reason_low_num_patients_code",
            "rate_of_experince_code",
        )

    def create(self, validated_data):
        with transaction.atomic():
            reason_low_num_patients_code = validated_data.pop(
                "reason_low_num_patients_code"
            )
            rate_of_experince_code = validated_data.pop("rate_of_experince_code")
            feedback = MicsPercevalFeedback.objects.create(**validated_data)
            feedback.reason_low_num_patients = Reason.objects.get(
                code=reason_low_num_patients_code
            )
            feedback.rate_of_experince = Rating.objects.get(code=rate_of_experince_code)
            feedback.save()
            return feedback

    def update(self, instance, validated_data):
        try:
            instance.num_of_patients = validated_data.get(
                "num_of_patients", instance.num_of_patients
            )
            instance.is_advance = validated_data.get("is_advance", instance.is_advance)
            instance.implanted_patient = validated_data.get(
                "implanted_patient", instance.implanted_patient
            )
            instance.implanted_perceval = validated_data.get(
                "instance.implanted_perceval", instance.implanted_perceval
            )
            instance.is_trainee_implant = validated_data.get(
                "is_trainee_implant", instance.is_trainee_implant
            )
            instance.any_leason = validated_data.get("any_leason", instance.any_leason)
            instance.report = validated_data.get("report", instance.report)

            if "reason_low_num_patients_code" in validated_data.keys():
                reason_low_num_patients_code = validated_data.pop(
                    "reason_low_num_patients_code"
                )
                validated_data["reason_low_num_patients"] = Reason.objects.get(
                    code=reason_low_num_patients_code
                )
                instance.reason_low_num_patients = validated_data.get(
                    "reason_low_num_patients", instance.reason_low_num_patients
                )

            if "rate_of_experince_code" in validated_data.keys():
                rate_of_experince_code = validated_data.pop("rate_of_experince_code")
                validated_data["rate_of_experince"] = Rating.objects.get(
                    code=rate_of_experince_code
                )
                instance.rate_of_experince = validated_data.get(
                    "rate_of_experince", instance.rate_of_experince
                )

            instance.save()
            return instance
        except Exception as e:
            return e

    def get_reason_low_num_patients(self, obj):
        try:
            return obj.reason_low_num_patients.code
        except:
            return None

    def get_rate_of_experince(self, obj):
        try:
            return obj.rate_of_experince.code
        except:
            return None

    def get_proctorship(self, obj):
        try:
            return obj.proctorship.id
        except:
            return None


class MicsTraineeFeedbackSerializer(serializers.ModelSerializer):
    trainee = serializers.SerializerMethodField(read_only=True)
    implanted_perceval = serializers.IntegerField(required=True)
    rate_of_experince = serializers.SerializerMethodField(read_only=True)
    rate_of_training = serializers.CharField(read_only=True)
    need_further_training = serializers.BooleanField(required=True)
    plan_for_next = serializers.CharField(required=True)
    any_sugestion = serializers.CharField(required=True)
    report = serializers.FileField(required=True)
    is_memo_family = serializers.BooleanField(required=True)
    perceval_driver = serializers.CharField(
        required=True, allow_null=True, allow_blank=True
    )
    trainee_id = serializers.IntegerField(write_only=True)
    rate_of_experince_code = serializers.CharField(write_only=True)
    rate_of_training_code = serializers.CharField(write_only=True)
    is_solo_smart = serializers.BooleanField(required=True)
    is_perceval = serializers.BooleanField(required=True)
    activity_id = serializers.SerializerMethodField(read_only=True)
    number_patient = serializers.IntegerField(required=True)

    class Meta:
        model = MicsTraineeFeedback
        fields = (
            "id",
            "number_patient",
            "trainee",
            "activity_id",
            "implanted_perceval",
            "rate_of_experince",
            "rate_of_training",
            "need_further_training",
            "plan_for_next",
            "any_sugestion",
            "perceval_driver",
            "report",
            "is_memo_family",
            "is_perceval",
            "is_solo_smart",
            "trainee_id",
            "rate_of_training_code",
            "rate_of_experince_code",
        )

    def create(self, validated_data):
        with transaction.atomic():
            rate_of_training_code = validated_data.pop("rate_of_training_code")
            rate_of_experince_code = validated_data.pop("rate_of_experince_code")
            feedback = MicsTraineeFeedback.objects.create(**validated_data)
            feedback.rate_of_training = Rating.objects.get(code=rate_of_training_code)
            feedback.rate_of_experince = Rating.objects.get(code=rate_of_experince_code)
            feedback.save()
            return feedback

    def update(self, instance, validated_data):
        try:
            instance.implanted_perceval = validated_data.get(
                "implanted_perceval", instance.implanted_perceval
            )
            instance.rate_of_experince = validated_data.get(
                "rate_of_experince", instance.rate_of_experince
            )
            instance.rate_of_training = validated_data.get(
                "rate_of_training", instance.rate_of_training
            )
            instance.need_further_training = validated_data.get(
                "need_further_training", instance.need_further_training
            )
            instance.plan_for_next = validated_data.get(
                "plan_for_next", instance.plan_for_next
            )
            instance.any_sugestion = validated_data.get(
                "any_sugestion", instance.any_sugestion
            )

            if "report" in validated_data.keys():
                instance.report = validated_data.get("report", instance.report)

            instance.perceval_driver = validated_data.get(
                "perceval_driver", instance.perceval_driver
            )

            if "rate_of_experince_code" in validated_data.keys():
                rate_of_experince_code = validated_data.pop("rate_of_experince_code")
                validated_data["rate_of_experince"] = Rating.objects.get(
                    code=rate_of_experince_code
                )
                instance.rate_of_experince = validated_data.get(
                    "rate_of_experince", instance.rate_of_experince
                )

            if "rate_of_training_code" in validated_data.keys():
                rate_of_training_code = validated_data.pop("rate_of_training_code")
                validated_data["rate_of_training"] = Rating.objects.get(
                    code=rate_of_training_code
                )
                instance.rate_of_training = validated_data.get(
                    "rate_of_training", instance.rate_of_experince
                )

            instance.number_patient = validated_data.get(
                "number_patient", instance.number_patient
            )
            instance.save()
            return instance
        except Exception as e:
            return e

    def get_rate_of_experince(self, obj):
        try:
            return obj.rate_of_experince.name
        except:
            return None

    def get_trainee(self, obj):
        try:
            return obj.trainee.id
        except:
            return None

    def get_activity_id(self, obj):
        try:
            return obj.trainee.proctorship.id
        except:
            return None


class MicsInvoiceSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    invoice_number = serializers.CharField(required=True)
    fee_covered = serializers.CharField(required=True)
    other_cost = serializers.CharField(required=True)
    invoice_date = serializers.DateField(required=True)
    note = serializers.CharField(required=True, allow_null=True, allow_blank=True)
    invoice_sent = serializers.BooleanField(required=True, allow_null=True)

    class Meta:
        model = MicsInvoice
        fields = [
            "id",
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
                invoice = MicsInvoice.objects.create(**validated_data)
                invoice.save()
                return invoice
        except Exception as e:
            return None

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


class MicsAttendanceFormSerailizers(serializers.ModelSerializer):
    attendance_form = serializers.FileField(required=True)

    class Meta:
        model = MicsAttendanceForm
        fields = ["id", "attendance_form"]

    def create(self, validated_data):
        try:
            with transaction.atomic():
                attendace_form = MicsAttendanceForm.objects.create(**validated_data)
                attendace_form.save()
                return attendace_form
        except Exception as e:
            return None

    def update(self, instance, validated_data):
        try:
            instance.attendance_form = validated_data.get(
                "attendance_form", instance.attendance_form
            )
            instance.save()
            return instance
        except Exception as e:
            return e


class MicsCertificateFormSerailizers(serializers.ModelSerializer):
    certificate = serializers.FileField(required=True)

    class Meta:
        model = MicsProctorshipCertificateForm
        fields = ["id", "certificate"]

    def create(self, validated_data):
        try:
            with transaction.atomic():
                attendace_form = MicsProctorshipCertificateForm.objects.create(
                    **validated_data
                )
                attendace_form.save()
                return attendace_form
        except Exception as e:
            return None

    def update(self, instance, validated_data):
        try:
            instance.certificate = validated_data.get(
                "certificate", instance.certificate
            )
            instance.save()
            return instance
        except Exception as e:
            return e
