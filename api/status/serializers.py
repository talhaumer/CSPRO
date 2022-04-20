from collections import OrderedDict

from django.db import transaction
from rest_framework import serializers

from api.proctors.models import Proctors
from api.status.models import ProctorshipProctors, Proposal, Status, StatusConstantData


class ProctorshipProctorsSerializer(serializers.ModelSerializer):
    proctors = serializers.SerializerMethodField(read_only=True)
    status = serializers.BooleanField(read_only=True)
    proctor_order = serializers.IntegerField(read_only=True)

    class Meta:
        model = ProctorshipProctors
        fields = ["proctors", "status", "proctor_order"]

    def get_proctors(self, obj):
        try:
            return obj.proctors.user.name
        except:
            return None


class AlternativeSerializer(serializers.ModelSerializer):
    proctor_user_id = serializers.IntegerField(write_only=True)
    start_date = serializers.DateField(required=True)
    end_date = serializers.DateField(required=True)
    note = serializers.CharField(required=True, allow_null=True, allow_blank=True)
    proctors = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Proposal
        fields = ["id", "proctor_user_id", "note", "end_date", "start_date", "proctors"]

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
            return ProctorshipProctorsSerializer(
                obj.proctor_porposal.proctors, many=True
            ).data
        except:
            return None


class AlternativeViewSerializer(serializers.ModelSerializer):
    proctor = serializers.SerializerMethodField(read_only=True)
    start_date = serializers.DateField(required=True)
    end_date = serializers.DateField(required=True)
    note = serializers.CharField(required=True, allow_null=True, allow_blank=True)

    class Meta:
        model = Proposal
        fields = ["id", "proctor", "note", "end_date", "start_date"]

    def get_proctor(self, obj):
        try:
            return ProctorshipProctorsSerializer(
                obj.proctor_porposal.all(), many=True
            ).data
        except:
            return None


class StatusSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField(read_only=True)
    status = serializers.CharField(required=True)
    user_id = serializers.IntegerField(write_only=True)
    proctorship_activity_id = serializers.IntegerField(write_only=True)
    date = serializers.DateField(read_only=True)
    purposal = serializers.SerializerMethodField(read_only=True)
    alternatives_data = AlternativeSerializer(required=False)
    code = serializers.CharField(read_only=True)
    reason = serializers.CharField(required=False)

    class Meta:
        model = Status
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
                alternatives_data = OrderedDict()
                if "alternatives_data" in validated_data.keys():
                    alternatives_data = validated_data.pop("alternatives_data")

                proctorship_activity_id = validated_data.pop("proctorship_activity_id")
                validated_data["proctorship_activity_id"] = proctorship_activity_id
                Status.objects.filter(
                    proctorship_activity__id=proctorship_activity_id
                ).update(is_active=False)
                status = validated_data.pop("status")
                user_id = validated_data.pop("user_id")
                validated_data["user_id"] = user_id
                validated_data["status"] = StatusConstantData.objects.get(code=status)
                status = Status.objects.create(**validated_data)

                if len(alternatives_data) != 0:
                    data_add = {
                        "status": status,
                        "note": alternatives_data["note"],
                        "start_date": alternatives_data["start_date"],
                        "end_date": alternatives_data["end_date"],
                    }
                    alt = Proposal.objects.create(**data_add)
                    if "proctor_user_id" in alternatives_data.keys():
                        qs = ProctorshipProctors.objects.filter(
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
                        ProctorshipProctors.objects.create(**proctors)

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
            return AlternativeViewSerializer(obj.alter_proctorship_porposal.get()).data
        except:
            return None


class StatusViewSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField(read_only=True)
    status = serializers.SerializerMethodField(read_only=True)
    code = serializers.SerializerMethodField(read_only=True)
    date = serializers.DateField(read_only=True)
    reason = serializers.CharField(read_only=True)
    alternatives = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Status
        fields = ["id", "user", "status", "code", "date", "alternatives", "reason"]

    def get_user(self, obj):
        try:
            return obj.user.name
        except:
            return None

    def get_alternatives(self, obj):
        try:
            return AlternativeViewSerializer(obj.alter_proctorship_porposal.get()).data
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


class ConstantStatusDataSerializer(serializers.ModelSerializer):
    name = serializers.CharField(read_only=True)
    code = serializers.SlugField(read_only=True)

    class Meta:
        model = StatusConstantData
        fields = ["name", "code"]


class ProposalDateUpdateSerializer(serializers.ModelSerializer):
    start_date = serializers.DateField(required=True)
    end_date = serializers.DateField(required=True)

    class Meta:
        model = Proposal
        fields = ["start_date", "end_date"]

    def update(self, instance, validated_data):
        try:
            instance.start_date = validated_data.get("start_date", instance.start_date)
            instance.end_date = validated_data.get("end_date", instance.end_date)
            instance.save()
            return instance
        except Exception as e:
            return e


class StatusTestingSerializer(serializers.ModelSerializer):
    status = serializers.CharField(required=True)
    proctorship_activity_id = serializers.IntegerField(write_only=True)
    date = serializers.DateField(read_only=True)
    code = serializers.CharField(read_only=True)
    reason = serializers.CharField(required=False)

    class Meta:
        model = Status
        fields = ["id", "status", "reason", "proctorship_activity_id", "code", "date"]

    def create(self, validated_data):
        try:
            with transaction.atomic():
                status = validated_data.pop("status")
                validated_data["status"] = StatusConstantData.objects.get(code=status)
                status = Status.objects.create(**validated_data)
                status.save()
                return status
        except Exception as e:
            return e
