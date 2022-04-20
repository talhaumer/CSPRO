from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone

from api.models import (
    AreaOfExperties,
    Audience,
    EventType,
    Hcp_role,
    Hospital,
    Languages,
    Region,
    Solution,
    Speciality,
)
from api.proctors.models import Proctors
from api.status.models import StatusConstantData
from api.users.models import User
from api.zone.models import Countries
from main.models import Base

# Create your models here.


class Event(Base):
    event_country = models.ForeignKey(
        Countries,
        db_column="EventCountryId",
        on_delete=models.CASCADE,
        related_name="event_country",
        default=None,
    )
    agenda = models.FileField(
        upload_to="uploads/", db_column="Agenda", null=True, blank=True
    )
    no_speach = models.BooleanField(default=False, db_column="NoSpeechRequested")
    is_global = models.BooleanField(default=False, db_column="Area")
    activity_id = models.CharField(
        db_column="ActivityID", default=None, null=True, blank=True, max_length=255
    )
    meeting_docs = models.FileField(
        upload_to="uploads/", db_column="MeetingDocs", null=True, blank=True
    )

    class Meta:
        db_table = "Event"


class EventStatus(Base):
    user = models.ForeignKey(
        User,
        db_column="UserId",
        default=None,
        related_name="event_status_user",
        on_delete=models.CASCADE,
        null=True,
    )
    status = models.ForeignKey(
        StatusConstantData,
        related_name="event_status_data",
        db_column="EventStatus",
        default=None,
        null=True,
        on_delete=models.CASCADE,
    )
    event = models.ForeignKey(
        Event,
        db_column="EventId",
        related_name="event_status_event",
        default=None,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )
    date = models.DateField(auto_now_add=True, db_column="Date")
    timestamp = models.DateTimeField(default=timezone.now, db_column="TimeStamp")
    reason = models.CharField(
        default="", db_column="Reason", max_length=255, blank=True, null=True
    )
    is_active = models.BooleanField(default=True, db_column="IsActive")

    class Meta:
        db_table = "EventStatus"


class SpeakingEvent(Base):
    event_status = models.ForeignKey(
        EventStatus,
        db_column="EventDetail",
        related_name="event_status",
        null=True,
        on_delete=models.CASCADE,
        default=None,
    )
    start_date = models.DateField(default="", db_column="EventStartDate")
    end_date = models.DateField(default="", db_column="EventEndDate")
    event_name = models.CharField(db_column="EventNameId", max_length=255, default="")
    event_type = models.ForeignKey(
        EventType,
        db_column="EventType",
        on_delete=models.CASCADE,
        related_name="event_type_speaking_event",
        default=None,
    )
    event_location = models.CharField(
        max_length=255, db_column="EventLocation", default=""
    )
    solution = models.ManyToManyField(
        Solution,
        related_name="speakers_solution",
        db_column="SolutionSpeakerID",
        blank=True,
    )
    language = models.ManyToManyField(
        Languages,
        related_name="speakers_language",
        db_column="languageSpeakerID",
        blank=True,
    )
    participants = models.IntegerField(db_column="Participants", default=None)
    audience_type = models.ManyToManyField(
        Audience,
        related_name="speaking_event_audience",
        db_column="SpeakingEventAudienceTypeID",
        blank=True,
    )
    audience_region = models.ManyToManyField(
        Region,
        related_name="speaking_event_region",
        db_column="SpeakingEventAudienceRegionID",
        blank=True,
    )
    notes = models.TextField(db_column="Notes")

    class Meta:
        db_table = "SpeakingEvent"


class Speaker(Base):
    event = models.ForeignKey(
        Event,
        db_column="SpeakingEventSpeakerId",
        related_name="event_speaker",
        on_delete=models.CASCADE,
        default=None,
    )
    speaker_role = models.ForeignKey(
        Hcp_role,
        db_column="RoleSpeakerID",
        default=None,
        related_name="speaker_role",
        on_delete=models.CASCADE,
    )
    specialty = models.ForeignKey(
        Speciality,
        db_column="SpeakerSpecialtyID",
        related_name="speaker_specialty",
        default=None,
        on_delete=models.CASCADE,
        null=True,
    )
    title = models.CharField(
        max_length=255, null=True, blank=True, db_column="Title", default=""
    )
    duration = models.IntegerField(db_column="Duration", default=None, null=True)
    speech_focus = models.ForeignKey(
        AreaOfExperties,
        db_column="SpeakerSpeachFocusID",
        related_name="speaker_speech_focus",
        on_delete=models.CASCADE,
        default=None,
        null=True,
    )
    proctor = models.ForeignKey(
        Proctors,
        db_column="HCPSpeakerID",
        related_name="speaker_hcp",
        default=None,
        on_delete=models.CASCADE,
        null=True,
    )
    notes = models.TextField(db_column="Notes")
    other_proctor = models.CharField(
        max_length=255, null=True, blank=True, db_column="OtherNotListed", default=""
    )
    name_employee = models.CharField(
        max_length=255, null=True, blank=True, db_column="NameOfEmployee", default=""
    )
    depart_employee = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        db_column="DepartmentOfEmployee",
        default="",
    )
    focus_not_listed = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        db_column="SpeechFocusNotListed",
        default="",
    )
    new_mics = models.BooleanField(default=False, db_column="NewMics")
    signed_letter = models.FileField(
        upload_to="uploads/",
        db_column="SignedLetter",
        null=True,
        blank=True,
        default=None,
    )
    revoke = models.BooleanField(default=False, db_column="Revoke")
    status = models.BooleanField(default=False, db_column="Status")

    class Meta:
        db_table = "Speaker"


class SpeakingEventFeedBack(Base):
    event = models.ForeignKey(
        Event,
        db_column="EventId",
        related_name="event_feedback",
        default=None,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )
    speaker = models.ForeignKey(
        Speaker,
        db_column="SpeakerId",
        related_name="speaking_event_feedback",
        default=None,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )
    specialty = models.ForeignKey(
        Speciality,
        db_column="SpeakingFeedBackSpecialtyID",
        related_name="speaking_feedback_specialty",
        default=None,
        on_delete=models.CASCADE,
        null=True,
    )
    country = models.ForeignKey(
        Countries,
        db_column="EventFeedbackCountryId",
        on_delete=models.CASCADE,
        related_name="feedback_country",
        default=None,
    )
    rate_event = models.IntegerField(
        default=0,
        validators=[MaxValueValidator(4), MinValueValidator(1)],
        db_column="RateEvent",
    )
    rate_logistic_organization = models.IntegerField(
        default=0,
        validators=[MaxValueValidator(4), MinValueValidator(1)],
        db_column="RateTheLogisticOrganization",
    )
    scientific_content = models.IntegerField(
        default=0,
        validators=[MaxValueValidator(4), MinValueValidator(1)],
        db_column="ScientificContent",
    )
    message = models.TextField(db_column="Message", null=True, blank=True)
    suggestions = models.TextField(db_column="Suggestions", null=True, blank=True)

    class Meta:
        db_table = "SpeakingEventFeedBack"


class TopicRating(Base):
    speaker = models.ForeignKey(
        Speaker,
        db_column="SpeakerId",
        related_name="speaker_event_feedback_rating",
        default=None,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )
    speaking_event_feedBack = models.ForeignKey(
        SpeakingEventFeedBack,
        db_column="SpeakingEventFeedBackId",
        related_name="speaking_event_feedback_rating",
        default=None,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )
    rate_topic = models.IntegerField(
        default=0,
        validators=[MaxValueValidator(4), MinValueValidator(1)],
        db_column="RateTopic",
    )

    class Meta:
        db_table = "TopicRating"


class AttendanceFormSpeakingEvent(Base):
    attendance_form = models.FileField(
        db_column="AttendanceForm",
        upload_to="uploads/",
        null=True,
        blank=True,
        default=None,
    )
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name="event_attendance_form",
        db_column="EventID",
        default=None,
        null=True,
    )

    class Meta:
        db_table = "AttendanceFormSpeakingEvent"


class CognosId(Base):
    cognos = models.ManyToManyField(
        Hospital, related_name="cognos_id_speaker", db_column="CognosID", default=None
    )
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name="event_cognos_id",
        db_column="EventCognosID",
        default=None,
        null=True,
    )

    class Meta:
        db_table = "CognosId"
