from django.db import transaction
from rest_framework import serializers

from api.invoice.models import AttendanceForm, Invoice


class InvoiceSerializer(serializers.ModelSerializer):
    proctorship_id = serializers.IntegerField(write_only=True)
    invoice_number = serializers.CharField(required=True)
    fee_covered = serializers.CharField(required=True)
    other_cost = serializers.CharField(required=True)
    invoice_date = serializers.DateField(required=True)
    note = serializers.CharField(required=True, allow_null=True, allow_blank=True)
    invoice_sent = serializers.BooleanField(required=True, allow_null=True)

    class Meta:
        model = Invoice
        fields = [
            "proctorship_id",
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
                invoice = Invoice.objects.create(**validated_data)
                invoice.save()
                return invoice
        except Exception as e:
            return None


class AttendanceFormSerailizers(serializers.ModelSerializer):
    proctorship_id = serializers.IntegerField(write_only=True)
    attendance_form = serializers.FileField(required=True)

    class Meta:
        model = AttendanceForm
        fields = ["id", "proctorship_id", "attendance_form"]

    def create(self, validated_data):
        try:
            with transaction.atomic():
                attendace_form = AttendanceForm.objects.create(**validated_data)
                attendace_form.save()
                return attendace_form
        except Exception as e:
            return None


class AttendanceFormUpdateSerailizers(serializers.ModelSerializer):
    attendance_form = serializers.FileField(required=True)

    class Meta:
        model = AttendanceForm
        fields = ["id", "attendance_form"]

    def update(self, instance, validated_data):
        try:
            instance.attendance_form = validated_data.get(
                "attendance_form", instance.attendance_form
            )
            instance.save()
            return instance
        except Exception as e:
            return e


class InvoiceUpdateSerializer(serializers.ModelSerializer):
    invoice_number = serializers.CharField(required=True)
    fee_covered = serializers.CharField(required=True)
    other_cost = serializers.CharField(required=True)
    invoice_date = serializers.DateField(required=True)
    note = serializers.CharField(required=True, allow_null=True, allow_blank=True)
    invoice_sent = serializers.BooleanField(required=True, allow_null=True)

    class Meta:
        model = Invoice
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
