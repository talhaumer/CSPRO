import unicodedata

from django.db import models
from django.utils.text import slugify


class Base(models.Model):
    """Abstract model containing common fields."""

    created_by = models.BigIntegerField(
        db_column="CreatedBy", null=True, blank=True, default=0
    )
    created_on = models.DateTimeField(db_column="CreatedOn", auto_now_add=True)
    modified_by = models.BigIntegerField(
        db_column="ModifiedBy", default=0, null=True, blank=True
    )
    modified_on = models.DateTimeField(db_column="ModifiedOn", auto_now=True)
    deleted_by = models.BigIntegerField(
        db_column="DeletedBy", default=0, null=True, blank=True
    )
    deleted_on = models.DateTimeField(db_column="DeletedOn", auto_now=True)
    status = models.BigIntegerField(
        db_column="Status",
        default=0,
        help_text="Be default 0 which has no meaning this field is used for making the status like pending approved and for some other purpose",
    )

    class Meta:
        abstract = True
