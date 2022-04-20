# Generated by Django 3.1.7 on 2021-09-10 07:09

import django.core.validators
import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("zone", "0001_initial"),
        ("proctors", "0001_initial"),
        ("api", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="AttendanceFormSpeakingEvent",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "created_by",
                    models.BigIntegerField(
                        blank=True, db_column="CreatedBy", default=0, null=True
                    ),
                ),
                (
                    "created_on",
                    models.DateTimeField(auto_now_add=True, db_column="CreatedOn"),
                ),
                (
                    "modified_by",
                    models.BigIntegerField(
                        blank=True, db_column="ModifiedBy", default=0, null=True
                    ),
                ),
                (
                    "modified_on",
                    models.DateTimeField(auto_now=True, db_column="ModifiedOn"),
                ),
                (
                    "deleted_by",
                    models.BigIntegerField(
                        blank=True, db_column="DeletedBy", default=0, null=True
                    ),
                ),
                (
                    "deleted_on",
                    models.DateTimeField(auto_now=True, db_column="DeletedOn"),
                ),
                (
                    "status",
                    models.BigIntegerField(
                        db_column="Status",
                        default=0,
                        help_text="Be default 0 which has no meaning this field is used for making the status like pending approved and for some other purpose",
                    ),
                ),
                (
                    "attendance_form",
                    models.FileField(
                        blank=True,
                        db_column="AttendanceForm",
                        default=None,
                        null=True,
                        upload_to="uploads/",
                    ),
                ),
            ],
            options={
                "db_table": "AttendanceFormSpeakingEvent",
            },
        ),
        migrations.CreateModel(
            name="CognosId",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "created_by",
                    models.BigIntegerField(
                        blank=True, db_column="CreatedBy", default=0, null=True
                    ),
                ),
                (
                    "created_on",
                    models.DateTimeField(auto_now_add=True, db_column="CreatedOn"),
                ),
                (
                    "modified_by",
                    models.BigIntegerField(
                        blank=True, db_column="ModifiedBy", default=0, null=True
                    ),
                ),
                (
                    "modified_on",
                    models.DateTimeField(auto_now=True, db_column="ModifiedOn"),
                ),
                (
                    "deleted_by",
                    models.BigIntegerField(
                        blank=True, db_column="DeletedBy", default=0, null=True
                    ),
                ),
                (
                    "deleted_on",
                    models.DateTimeField(auto_now=True, db_column="DeletedOn"),
                ),
                (
                    "status",
                    models.BigIntegerField(
                        db_column="Status",
                        default=0,
                        help_text="Be default 0 which has no meaning this field is used for making the status like pending approved and for some other purpose",
                    ),
                ),
            ],
            options={
                "db_table": "CognosId",
            },
        ),
        migrations.CreateModel(
            name="Event",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "created_by",
                    models.BigIntegerField(
                        blank=True, db_column="CreatedBy", default=0, null=True
                    ),
                ),
                (
                    "created_on",
                    models.DateTimeField(auto_now_add=True, db_column="CreatedOn"),
                ),
                (
                    "modified_by",
                    models.BigIntegerField(
                        blank=True, db_column="ModifiedBy", default=0, null=True
                    ),
                ),
                (
                    "modified_on",
                    models.DateTimeField(auto_now=True, db_column="ModifiedOn"),
                ),
                (
                    "deleted_by",
                    models.BigIntegerField(
                        blank=True, db_column="DeletedBy", default=0, null=True
                    ),
                ),
                (
                    "deleted_on",
                    models.DateTimeField(auto_now=True, db_column="DeletedOn"),
                ),
                (
                    "status",
                    models.BigIntegerField(
                        db_column="Status",
                        default=0,
                        help_text="Be default 0 which has no meaning this field is used for making the status like pending approved and for some other purpose",
                    ),
                ),
                (
                    "agenda",
                    models.FileField(
                        blank=True, db_column="Agenda", null=True, upload_to="uploads/"
                    ),
                ),
                (
                    "no_speach",
                    models.BooleanField(db_column="NoSpeechRequested", default=False),
                ),
                ("is_global", models.BooleanField(db_column="Area", default=False)),
            ],
            options={
                "db_table": "Event",
            },
        ),
        migrations.CreateModel(
            name="EventStatus",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "created_by",
                    models.BigIntegerField(
                        blank=True, db_column="CreatedBy", default=0, null=True
                    ),
                ),
                (
                    "created_on",
                    models.DateTimeField(auto_now_add=True, db_column="CreatedOn"),
                ),
                (
                    "modified_by",
                    models.BigIntegerField(
                        blank=True, db_column="ModifiedBy", default=0, null=True
                    ),
                ),
                (
                    "modified_on",
                    models.DateTimeField(auto_now=True, db_column="ModifiedOn"),
                ),
                (
                    "deleted_by",
                    models.BigIntegerField(
                        blank=True, db_column="DeletedBy", default=0, null=True
                    ),
                ),
                (
                    "deleted_on",
                    models.DateTimeField(auto_now=True, db_column="DeletedOn"),
                ),
                ("date", models.DateField(auto_now_add=True, db_column="Date")),
                (
                    "timestamp",
                    models.DateTimeField(
                        db_column="TimeStamp", default=django.utils.timezone.now
                    ),
                ),
                (
                    "reason",
                    models.CharField(
                        blank=True,
                        db_column="Reason",
                        default="",
                        max_length=255,
                        null=True,
                    ),
                ),
                ("is_active", models.BooleanField(db_column="IsActive", default=True)),
                (
                    "event",
                    models.ForeignKey(
                        blank=True,
                        db_column="EventId",
                        default=None,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="event_status_event",
                        to="speakingevent.event",
                    ),
                ),
            ],
            options={
                "db_table": "EventStatus",
            },
        ),
        migrations.CreateModel(
            name="Speaker",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "created_by",
                    models.BigIntegerField(
                        blank=True, db_column="CreatedBy", default=0, null=True
                    ),
                ),
                (
                    "created_on",
                    models.DateTimeField(auto_now_add=True, db_column="CreatedOn"),
                ),
                (
                    "modified_by",
                    models.BigIntegerField(
                        blank=True, db_column="ModifiedBy", default=0, null=True
                    ),
                ),
                (
                    "modified_on",
                    models.DateTimeField(auto_now=True, db_column="ModifiedOn"),
                ),
                (
                    "deleted_by",
                    models.BigIntegerField(
                        blank=True, db_column="DeletedBy", default=0, null=True
                    ),
                ),
                (
                    "deleted_on",
                    models.DateTimeField(auto_now=True, db_column="DeletedOn"),
                ),
                (
                    "title",
                    models.CharField(
                        blank=True,
                        db_column="Title",
                        default="",
                        max_length=255,
                        null=True,
                    ),
                ),
                (
                    "duration",
                    models.IntegerField(db_column="Duration", default=None, null=True),
                ),
                ("notes", models.TextField(db_column="Notes")),
                (
                    "other_proctor",
                    models.CharField(
                        blank=True,
                        db_column="OtherNotListed",
                        default="",
                        max_length=255,
                        null=True,
                    ),
                ),
                (
                    "name_employee",
                    models.CharField(
                        blank=True,
                        db_column="NameOfEmployee",
                        default="",
                        max_length=255,
                        null=True,
                    ),
                ),
                (
                    "depart_employee",
                    models.CharField(
                        blank=True,
                        db_column="DepartmentOfEmployee",
                        default="",
                        max_length=255,
                        null=True,
                    ),
                ),
                (
                    "focus_not_listed",
                    models.CharField(
                        blank=True,
                        db_column="SpeechFocusNotListed",
                        default="",
                        max_length=255,
                        null=True,
                    ),
                ),
                ("new_mics", models.BooleanField(db_column="NewMics", default=False)),
                (
                    "signed_letter",
                    models.FileField(
                        blank=True,
                        db_column="SignedLetter",
                        default=None,
                        null=True,
                        upload_to="uploads/",
                    ),
                ),
                ("revoke", models.BooleanField(db_column="Revoke", default=False)),
                ("status", models.BooleanField(db_column="Status", default=False)),
                (
                    "event",
                    models.ForeignKey(
                        db_column="SpeakingEventSpeakerId",
                        default=None,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="event_speaker",
                        to="speakingevent.event",
                    ),
                ),
                (
                    "proctor",
                    models.ForeignKey(
                        db_column="HCPSpeakerID",
                        default=None,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="speaker_hcp",
                        to="proctors.proctors",
                    ),
                ),
                (
                    "speaker_role",
                    models.ForeignKey(
                        db_column="RoleSpeakerID",
                        default=None,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="speaker_role",
                        to="api.hcp_role",
                    ),
                ),
                (
                    "specialty",
                    models.ForeignKey(
                        db_column="SpeakerSpecialtyID",
                        default=None,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="speaker_specialty",
                        to="api.speciality",
                    ),
                ),
                (
                    "speech_focus",
                    models.ForeignKey(
                        db_column="SpeakerSpeachFocusID",
                        default=None,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="speaker_speech_focus",
                        to="api.areaofexperties",
                    ),
                ),
            ],
            options={
                "db_table": "Speaker",
            },
        ),
        migrations.CreateModel(
            name="SpeakingEventFeedBack",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "created_by",
                    models.BigIntegerField(
                        blank=True, db_column="CreatedBy", default=0, null=True
                    ),
                ),
                (
                    "created_on",
                    models.DateTimeField(auto_now_add=True, db_column="CreatedOn"),
                ),
                (
                    "modified_by",
                    models.BigIntegerField(
                        blank=True, db_column="ModifiedBy", default=0, null=True
                    ),
                ),
                (
                    "modified_on",
                    models.DateTimeField(auto_now=True, db_column="ModifiedOn"),
                ),
                (
                    "deleted_by",
                    models.BigIntegerField(
                        blank=True, db_column="DeletedBy", default=0, null=True
                    ),
                ),
                (
                    "deleted_on",
                    models.DateTimeField(auto_now=True, db_column="DeletedOn"),
                ),
                (
                    "status",
                    models.BigIntegerField(
                        db_column="Status",
                        default=0,
                        help_text="Be default 0 which has no meaning this field is used for making the status like pending approved and for some other purpose",
                    ),
                ),
                (
                    "rate_event",
                    models.IntegerField(
                        db_column="RateEvent",
                        default=0,
                        validators=[
                            django.core.validators.MaxValueValidator(4),
                            django.core.validators.MinValueValidator(1),
                        ],
                    ),
                ),
                (
                    "rate_logistic_organization",
                    models.IntegerField(
                        db_column="RateTheLogisticOrganization",
                        default=0,
                        validators=[
                            django.core.validators.MaxValueValidator(4),
                            django.core.validators.MinValueValidator(1),
                        ],
                    ),
                ),
                (
                    "scientific_content",
                    models.IntegerField(
                        db_column="ScientificContent",
                        default=0,
                        validators=[
                            django.core.validators.MaxValueValidator(4),
                            django.core.validators.MinValueValidator(1),
                        ],
                    ),
                ),
                (
                    "message",
                    models.TextField(blank=True, db_column="Message", null=True),
                ),
                (
                    "suggestions",
                    models.TextField(blank=True, db_column="Suggestions", null=True),
                ),
                (
                    "country",
                    models.ForeignKey(
                        db_column="EventFeedbackCountryId",
                        default=None,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="feedback_country",
                        to="zone.countries",
                    ),
                ),
                (
                    "event",
                    models.ForeignKey(
                        blank=True,
                        db_column="EventId",
                        default=None,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="event_feedback",
                        to="speakingevent.event",
                    ),
                ),
                (
                    "speaker",
                    models.ForeignKey(
                        blank=True,
                        db_column="SpeakerId",
                        default=None,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="speaking_event_feedback",
                        to="speakingevent.speaker",
                    ),
                ),
                (
                    "specialty",
                    models.ForeignKey(
                        db_column="SpeakingFeedBackSpecialtyID",
                        default=None,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="speaking_feedback_specialty",
                        to="api.speciality",
                    ),
                ),
            ],
            options={
                "db_table": "SpeakingEventFeedBack",
            },
        ),
        migrations.CreateModel(
            name="TopicRating",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "created_by",
                    models.BigIntegerField(
                        blank=True, db_column="CreatedBy", default=0, null=True
                    ),
                ),
                (
                    "created_on",
                    models.DateTimeField(auto_now_add=True, db_column="CreatedOn"),
                ),
                (
                    "modified_by",
                    models.BigIntegerField(
                        blank=True, db_column="ModifiedBy", default=0, null=True
                    ),
                ),
                (
                    "modified_on",
                    models.DateTimeField(auto_now=True, db_column="ModifiedOn"),
                ),
                (
                    "deleted_by",
                    models.BigIntegerField(
                        blank=True, db_column="DeletedBy", default=0, null=True
                    ),
                ),
                (
                    "deleted_on",
                    models.DateTimeField(auto_now=True, db_column="DeletedOn"),
                ),
                (
                    "status",
                    models.BigIntegerField(
                        db_column="Status",
                        default=0,
                        help_text="Be default 0 which has no meaning this field is used for making the status like pending approved and for some other purpose",
                    ),
                ),
                (
                    "rate_topic",
                    models.IntegerField(
                        db_column="RateTopic",
                        default=0,
                        validators=[
                            django.core.validators.MaxValueValidator(4),
                            django.core.validators.MinValueValidator(1),
                        ],
                    ),
                ),
                (
                    "speaker",
                    models.ForeignKey(
                        blank=True,
                        db_column="SpeakerId",
                        default=None,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="speaker_event_feedback_rating",
                        to="speakingevent.speaker",
                    ),
                ),
                (
                    "speaking_event_feedBack",
                    models.ForeignKey(
                        blank=True,
                        db_column="SpeakingEventFeedBackId",
                        default=None,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="speaking_event_feedback_rating",
                        to="speakingevent.speakingeventfeedback",
                    ),
                ),
            ],
            options={
                "db_table": "TopicRating",
            },
        ),
        migrations.CreateModel(
            name="SpeakingEvent",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "created_by",
                    models.BigIntegerField(
                        blank=True, db_column="CreatedBy", default=0, null=True
                    ),
                ),
                (
                    "created_on",
                    models.DateTimeField(auto_now_add=True, db_column="CreatedOn"),
                ),
                (
                    "modified_by",
                    models.BigIntegerField(
                        blank=True, db_column="ModifiedBy", default=0, null=True
                    ),
                ),
                (
                    "modified_on",
                    models.DateTimeField(auto_now=True, db_column="ModifiedOn"),
                ),
                (
                    "deleted_by",
                    models.BigIntegerField(
                        blank=True, db_column="DeletedBy", default=0, null=True
                    ),
                ),
                (
                    "deleted_on",
                    models.DateTimeField(auto_now=True, db_column="DeletedOn"),
                ),
                (
                    "status",
                    models.BigIntegerField(
                        db_column="Status",
                        default=0,
                        help_text="Be default 0 which has no meaning this field is used for making the status like pending approved and for some other purpose",
                    ),
                ),
                (
                    "start_date",
                    models.DateField(db_column="EventStartDate", default=""),
                ),
                ("end_date", models.DateField(db_column="EventEndDate", default="")),
                (
                    "event_name",
                    models.CharField(
                        db_column="EventNameId", default="", max_length=255
                    ),
                ),
                (
                    "event_location",
                    models.CharField(
                        db_column="EventLocation", default="", max_length=255
                    ),
                ),
                (
                    "participants",
                    models.IntegerField(db_column="Participants", default=None),
                ),
                ("notes", models.TextField(db_column="Notes")),
                (
                    "audience_region",
                    models.ManyToManyField(
                        blank=True,
                        db_column="SpeakingEventAudienceRegionID",
                        related_name="speaking_event_region",
                        to="api.Region",
                    ),
                ),
                (
                    "audience_type",
                    models.ManyToManyField(
                        blank=True,
                        db_column="SpeakingEventAudienceTypeID",
                        related_name="speaking_event_audience",
                        to="api.Audience",
                    ),
                ),
                (
                    "event_status",
                    models.ForeignKey(
                        db_column="EventDetail",
                        default=None,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="event_status",
                        to="speakingevent.eventstatus",
                    ),
                ),
                (
                    "event_type",
                    models.ForeignKey(
                        db_column="EventType",
                        default=None,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="event_type_speaking_event",
                        to="api.eventtype",
                    ),
                ),
                (
                    "language",
                    models.ManyToManyField(
                        blank=True,
                        db_column="languageSpeakerID",
                        related_name="speakers_language",
                        to="api.Languages",
                    ),
                ),
                (
                    "solution",
                    models.ManyToManyField(
                        blank=True,
                        db_column="SolutionSpeakerID",
                        related_name="speakers_solution",
                        to="api.Solution",
                    ),
                ),
            ],
            options={
                "db_table": "SpeakingEvent",
            },
        ),
    ]
