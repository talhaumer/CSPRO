# Generated by Django 3.1.7 on 2021-09-10 07:09

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("proctors", "0001_initial"),
        ("api", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("feedback", "0002_auto_20210910_1209"),
        ("zone", "0001_initial"),
        ("masterproctorship", "0003_masterproctorshipstatus_status"),
    ]

    operations = [
        migrations.AddField(
            model_name="masterproctorshipstatus",
            name="user",
            field=models.ForeignKey(
                db_column="UserId",
                default=None,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="master_proctorship_status_user",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="masterproctorshipproposal",
            name="status",
            field=models.ForeignKey(
                blank=True,
                db_column="StatusId",
                default=None,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="alter_master_proctorship_porposal",
                to="masterproctorship.masterproctorshipstatus",
            ),
        ),
        migrations.AddField(
            model_name="masterproctorshipproctors",
            name="master_proctorship_proposal",
            field=models.ForeignKey(
                db_column="MasterProctorshipProposalID",
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="master_proctorship_porposal",
                to="masterproctorship.masterproctorshipproposal",
            ),
        ),
        migrations.AddField(
            model_name="masterproctorshipproctors",
            name="proctors",
            field=models.ForeignKey(
                db_column="ProctorsID",
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="master_proctorship_proctor_data",
                to="proctors.proctors",
            ),
        ),
        migrations.AddField(
            model_name="masterproctorshipproctorreport",
            name="master_proctorship_trainee",
            field=models.ForeignKey(
                blank=True,
                db_column="MasterProctorshipTraineeProfileId",
                default=None,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="master_proctorship_trainee_report",
                to="masterproctorship.masterproctorshiptraineeprofile",
            ),
        ),
        migrations.AddField(
            model_name="masterproctorshipproctorreport",
            name="rate_of_experince",
            field=models.ForeignKey(
                db_column="RateOfExperinceOfMaterProctorship",
                default=None,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="rate_of_experince_rating",
                to="feedback.rating",
            ),
        ),
        migrations.AddField(
            model_name="masterproctorshipfeedback",
            name="master_proctorship_activity",
            field=models.ForeignKey(
                blank=True,
                db_column="MasterProctorshipFeedBackId",
                default=None,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="master_proctorship_feedback",
                to="masterproctorship.masterproctorship",
            ),
        ),
        migrations.AddField(
            model_name="masterproctorshipfeedback",
            name="rate_of_level_support",
            field=models.ForeignKey(
                blank=True,
                db_column="RateOflevelOfSupport",
                default=None,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="rate_of_level_support_rating",
                to="feedback.rating",
            ),
        ),
        migrations.AddField(
            model_name="masterproctorshipfeedback",
            name="rate_proctoring_experince",
            field=models.ForeignKey(
                blank=True,
                db_column="RateProctoringExperince",
                default=None,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="rate_procotring_rating",
                to="feedback.rating",
            ),
        ),
        migrations.AddField(
            model_name="masterproctorship",
            name="country",
            field=models.ForeignKey(
                blank=True,
                db_column="MasterProctorshipCountriesID",
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="masterproctorship_country",
                to="zone.countries",
            ),
        ),
        migrations.AddField(
            model_name="masterproctorship",
            name="hospital",
            field=models.ForeignKey(
                blank=True,
                db_column="MasterProctorshipHospitalID",
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="masterproctorship_hospital",
                to="api.hospital",
            ),
        ),
        migrations.AddField(
            model_name="masterproctorship",
            name="master_proctorship_type",
            field=models.ForeignKey(
                db_column="MasterProctorshipType",
                default=None,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="master_proctorship_constant",
                to="masterproctorship.masterproctorshipconstantdata",
            ),
        ),
        migrations.AddField(
            model_name="masterproctorship",
            name="user",
            field=models.ForeignKey(
                db_column="MasterProctorshipID",
                on_delete=django.db.models.deletion.CASCADE,
                related_name="masterproctorship_user",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="invoicemasterproctorship",
            name="master_proctorship",
            field=models.ForeignKey(
                db_column="MasterProctorShipID",
                default=None,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="master_proctorship_invoice",
                to="masterproctorship.masterproctorship",
            ),
        ),
        migrations.AddField(
            model_name="attendanceformmasterproctorship",
            name="master_proctorship",
            field=models.ForeignKey(
                db_column="MasterProctorShipID",
                default=None,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="master_proctorship_attendace",
                to="masterproctorship.masterproctorship",
            ),
        ),
    ]
