from django.db import models
from django.utils.text import slugify
from model_utils import Choices

from main.models import Base


# Create your models here.
class Countries(Base):
    name = models.CharField(max_length=100)
    code = models.SlugField(db_column="Code", default="")

    class Meta:
        db_table = "Countries"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        try:
            if not self.pk:
                self.code = slugify(self.name)
            super().save()
        except Exception:
            raise


class Zone(Base):
    name = models.CharField(
        max_length=255,
        db_column="ZoneName",
        default=None,
        unique=True,
        null=False,
        blank=False,
    )
    code = models.SlugField(db_column="Code", default="")
    status = models.BooleanField(db_column="ZoneStatus", default=True)

    class Meta:
        db_table = "Zone"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        try:
            if not self.pk:
                self.code = slugify(self.name)
            super().save()
        except Exception:
            raise


class ZoneCountries(Base):
    countries = models.ForeignKey(
        Countries,
        on_delete=models.CASCADE,
        db_column="CountriesID",
        related_name="zone_countires",
        null=True,
        blank=True,
    )
    zone = models.ForeignKey(
        Zone,
        on_delete=models.CASCADE,
        db_column="ZoneID",
        related_name="zone_zone_countires",
        null=True,
        blank=True,
    )
    status = models.BooleanField(default=True, db_column="ZoneStatus")

    class Meta:
        db_table = "ZoneCountries"


ORDER_COLUMN_CHOICES = Choices(
    ("0", "id"),
    ("1", "zone"),
)


def query_zone_by_args(query_object, **kwargs):
    try:
        draw = int(kwargs.get("draw", None)[0])
        length = int(kwargs.get("length", None)[0])
        start = int(kwargs.get("start", None)[0])
        search_value = kwargs.get("search[value]", None)[0]
        order_column = kwargs.get("order[0][column]", None)[0]
        order = kwargs.get("order[0][dir]", None)[0]
        order_column = ORDER_COLUMN_CHOICES[order_column]

        # django orm '-' -> desc
        if order == "desc":
            order_column = "-" + order_column

        queryset = Zone.objects.filter(query_object)

        total = queryset.count()
        if search_value:
            queryset = queryset.filter(
                Q(id__icontains=search_value) | Q(zone__icontains=search_value)
            )
        count = queryset.count()
        queryset = queryset.order_by(order_column)[start : start + length]
        return {"items": queryset, "count": count, "total": total, "draw": draw}
    except Exception as e:
        print(e)
        return None
