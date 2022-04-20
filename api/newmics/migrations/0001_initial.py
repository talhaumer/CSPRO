# Generated by Django 3.1.7 on 2021-09-10 07:09

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="MicsPreceptorship",
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
                ("note", models.TextField(db_column="Note")),
            ],
            options={
                "db_table": "MicsPreceptorship",
            },
        ),
        migrations.CreateModel(
            name="MicsPreceptorshipProctors",
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
                    models.BooleanField(
                        db_column="PreceptorshipProctorStatus", default=True
                    ),
                ),
            ],
            options={
                "db_table": "MicsPreceptorshipProctors",
            },
        ),
        migrations.CreateModel(
            name="MicsPreceptorshipProposal",
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
                ("note", models.TextField(db_column="Note", default="")),
                ("start_date", models.DateField(db_column="StartDate", default=None)),
                ("end_date", models.DateField(db_column="EndDate", default=False)),
            ],
            options={
                "db_table": "MicsPreceptorshipProposal",
            },
        ),
        migrations.CreateModel(
            name="MicsPreceptorshipStatus",
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
            ],
            options={
                "db_table": "MicsPreceptorshipStatus",
            },
        ),
        migrations.CreateModel(
            name="MicsProctorship",
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
                    "hotel",
                    models.CharField(db_column="HotelName", default="", max_length=255),
                ),
                (
                    "number_of_cases",
                    models.IntegerField(
                        blank=True, db_column="NumberOfCases", default=None, null=True
                    ),
                ),
                (
                    "transplant_time",
                    models.CharField(
                        blank=True,
                        db_column="TransplantTime",
                        default="",
                        max_length=255,
                        null=True,
                    ),
                ),
                (
                    "is_second",
                    models.BooleanField(db_column="IsSecondProctorship", default=False),
                ),
            ],
            options={
                "db_table": "MicsProctorship",
            },
        ),
        migrations.CreateModel(
            name="MicsProctorshipProctors",
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
                    models.BooleanField(
                        db_column="ProctorshipProctorStatus", default=True
                    ),
                ),
                (
                    "proctor_order",
                    models.IntegerField(db_column="Order", default=None, null=True),
                ),
            ],
            options={
                "db_table": "MicsProctorshipProctors",
            },
        ),
        migrations.CreateModel(
            name="MicsProctorshipProposal",
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
                ("note", models.TextField(db_column="Note", default="")),
                ("start_date", models.DateField(db_column="StartDate", default=None)),
                ("end_date", models.DateField(db_column="EndDate", default=False)),
            ],
            options={
                "db_table": "MicsProctorshipProposal",
            },
        ),
        migrations.CreateModel(
            name="MicsProctorshipStatus",
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
            ],
            options={
                "db_table": "MicsProctorshipStatus",
            },
        ),
        migrations.CreateModel(
            name="MicsTraineeProfile",
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
                    "name",
                    models.CharField(db_column="Name", default="", max_length=255),
                ),
                (
                    "surname",
                    models.CharField(db_column="SurName", default="", max_length=255),
                ),
                (
                    "corcym_accompanying_rep",
                    models.CharField(
                        blank=True,
                        db_column="CorcymAccompanyingRep",
                        default="",
                        max_length=255,
                        null=True,
                    ),
                ),
                ("mvr_case_per_year", models.IntegerField(db_column="MVRCasePerYear")),
                (
                    "mvr_case_per_year_by_trainee",
                    models.IntegerField(db_column="MVRCasePerYearByTrainee"),
                ),
                ("note", models.TextField(db_column="Note")),
                ("status", models.BooleanField(db_column="Status", default=False)),
                ("revoke", models.BooleanField(db_column="Revoke", default=False)),
                (
                    "interest_invasive",
                    models.BooleanField(db_column="InterestInvasive", default=False),
                ),
            ],
            options={
                "db_table": "MicsTraineeProfile",
            },
        ),
        migrations.CreateModel(
            name="NewMics",
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
                ("is_rat", models.BooleanField(db_column="TypeOfMics", default=False)),
            ],
            options={
                "db_table": "NewMics",
            },
        ),
    ]
