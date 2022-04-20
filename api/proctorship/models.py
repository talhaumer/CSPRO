from django.db import models
from django.utils.text import slugify

from api.models import Hcp_role, Hospital, Products
from api.proctors.models import Proctors
from api.users.models import User
from api.zone.models import Countries, Zone, ZoneCountries
from main.models import Base


class TypeOfTraining:
    FIRST_TRAINING = 100
    TO_OPEN_NEW_CENTER = 101
    ADVANCE_TRAINING = 500
    OTHER_ADVANCE_TRAINING = 501
    IMPLANT_REGULARLY = 502
    NOT_IMPLANT_REGULARLY = 503
    TRAINING_AFTER_COMPLAINT = 600
    PROCTORSHIP_AFTER_10_CASES = 700

    FIRST_TRAINING_CODE = "first_training"
    ADVANCE_TRAINING_CODE = "advance_training"
    TO_OPEN_NEW_CENTER_CODE = "to_open_new_center"
    OTHER_ADVANCE_TRAINING_CODE = "other_advance_training"
    IMPLANT_REGULARLY_CODE = "implant_regulary"
    NOT_IMPLANT_REGULARLY_CODE = "not_implant_regularly"
    TRAINING_AFTER_COMPLAINT_CODE = "training_after_complaint"
    PROCTORSHIP_AFTER_10_CASES_CODE = "proctorship_after_10_cases"


class ConstantData(Base):
    name = models.CharField(max_length=255, db_column="Name", default="")
    code = models.SlugField(db_column="Code", default="")
    type = models.CharField(db_column="Type", max_length=255, default="")
    field = models.CharField(db_column="Field", default="", max_length=255)

    class Meta:
        db_table = "ConstantData"

    def __str__(self):
        return self.code

    def save(self, *args, **kwargs):
        try:
            if not self.pk:
                self.code = slugify(self.name)
            super().save()
        except Exception:
            raise


# Create your models here.


class Proctorship(Base):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="proctorship_user",
        db_column="ProctorshipUserID",
    )
    country = models.ForeignKey(
        Countries,
        db_column="CountriesProctorshipID",
        null=True,
        on_delete=models.CASCADE,
        related_name="proctorship_country",
        default=None,
    )
    hospital = models.ForeignKey(
        Hospital,
        db_column="HospitalProctorshipID",
        null=True,
        on_delete=models.CASCADE,
        related_name="proctorship_hospital",
        default=None,
    )
    product = models.ForeignKey(
        Products,
        db_column="ProductID",
        null=True,
        related_name="proctorship_product",
        on_delete=models.CASCADE,
        default=None,
    )
    secondary_product = models.ForeignKey(
        Products,
        db_column="SecondaryProductID",
        null=True,
        related_name="proctorship_secondary_product",
        on_delete=models.CASCADE,
        default=None,
    )
    note = models.TextField(db_column="Note")
    training_type = models.ForeignKey(
        ConstantData,
        db_column="TrainingType",
        related_name="training_Type_constantdata",
        default=None,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )
    new_center = models.ForeignKey(
        ConstantData,
        db_column="NewCenter",
        default=None,
        related_name="new_center_constantdata",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )
    types_of_first_training = models.ForeignKey(
        ConstantData,
        db_column="TypesOfFirstTraining",
        default=None,
        related_name="types_of_first_training_constantdata",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )
    type_advance_training = models.ForeignKey(
        ConstantData,
        related_name="type_advance_training_constantdata",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        default=None,
        db_column="TypesofAdvancedTraining",
    )
    memo_surgeon_implant = models.IntegerField(
        db_column="MemoSurgeonImplant", default=None, blank=True
    )
    other_advanced_training = models.ForeignKey(
        ConstantData,
        on_delete=models.CASCADE,
        db_column="OtherAdvancedTraining",
        default=None,
        null=True,
        blank=True,
    )
    specific_training = models.ForeignKey(
        ConstantData,
        related_name="specific_training_constantdata",
        db_column="SpecificTraining",
        default=None,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )
    not_implant_regularly = models.ForeignKey(
        ConstantData,
        on_delete=models.CASCADE,
        db_column="NotImplantRegularly",
        default=None,
        related_name="not_implant_regularly_constantdata",
        null=True,
        blank=True,
    )
    rechord_surgeon_implant = models.IntegerField(
        db_column="ReChordSurgeonImplant", default=None, blank=True
    )
    other_num_of_implants = models.IntegerField(
        null=True,
        blank=True,
        db_column="NumberOfPercevel",
    )
    ETQ_number = models.IntegerField(
        null=True,
        blank=True,
        default=None,
        db_column="ETQNumber",
    )
    issue = models.CharField(
        max_length=100, db_column="SpecificIssue", default="", null=True, blank=True
    )
    hotel = models.CharField(
        max_length=255,
        db_column="HotelName",
        default="",
    )
    number_of_cases = models.IntegerField(
        db_column="NumberOfCases", default=None, null=True, blank=True
    )
    transplant_time = models.CharField(
        db_column="TransplantTime", max_length=255, blank=True, null=True, default=""
    )

    field_check = models.CharField(
        default="", db_column="FieldForDataCheck", max_length=255
    )
    zone_countries = models.ForeignKey(
        ZoneCountries,
        on_delete=models.CASCADE,
        null=True,
        db_column="ProctorZoneID",
        related_name="proctor_zone_countries",
        default=None,
    )
    is_global = models.BooleanField(default=False, db_column="IsGlobal")
    note_related_to_proctor = models.TextField(
        db_column="NoteRelatedToProctors", default=None
    )
    first_proctorship_num = models.IntegerField(
        db_column="FirstPrcotorshipId", default=None, null=True, blank=True
    )
    activity_id = models.CharField(
        db_column="ActivityID", default=None, null=True, blank=True, max_length=255
    )

    class Meta:
        db_table = "Proctorship"
