from django.db import transaction
from django.utils.text import slugify
from rest_framework import serializers

from .models import Countries, Zone, ZoneCountries


class CountriesSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(required=True)

    class Meta:
        model = Countries
        fields = ["id", "name"]

    def create(self, validated_data):
        return Countries.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.name = validated_data.get("name", instance.name)
        instance.save()
        return instance


class CountriesZoneSerializers(serializers.SerializerMethodField):
    name = serializers.CharField(read_only=True)

    class Meta:
        model = ZoneCountries
        fields = ["name"]


class ZoneSerializer(serializers.ModelSerializer):
    name = serializers.CharField(required=True)
    countries_id = serializers.ListField(write_only=True)
    countries = serializers.SerializerMethodField(read_only=True)
    status = serializers.BooleanField(required=True)

    class Meta:
        model = Zone
        fields = ("id", "name", "countries_id", "countries", "status")

    def create(self, validated_data):
        with transaction.atomic():
            countries = validated_data.pop("countries_id")
            zone = Zone.objects.create(**validated_data)
            for country in countries:
                zone_countries = {
                    "countries": Countries.objects.get(id=country),
                    "zone": zone,
                }
                ZoneCountries.objects.create(**zone_countries)
            zone.save()
            return zone

    def get_countries(self, obj):
        try:
            arr = []
            for d in obj.zone_zone_countires.filter(status=True):
                arr.append(d.countries.name)
            return arr
        except:
            return None


class ZoneCountrySerializer(serializers.ModelSerializer):
    countries = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Zone
        fields = ["countries"]

    def get_countries(self, obj):
        try:
            arr = []
            for d in obj.zone_zone_countires.all():
                arr.append(d.countries.name)
            return arr
        except:
            return None


class UserZoneCountrySerializer(serializers.ModelSerializer):
    countries = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Zone
        fields = ["countries"]

    def get_countries(self, obj):
        try:
            arr = []
            for d in obj.zone_zone_countires.all():
                countries_data = {"name": d.countries.name, "id": d.countries.id}
                arr.append(countries_data)
            return arr
        except:
            return None


class ZoneNameUpdateView(serializers.ModelSerializer):
    name = serializers.CharField(required=False)
    status = serializers.BooleanField(required=False)

    class Meta:
        model = Zone
        fields = ["name", "status"]

    def update(self, instance, validated_data):
        try:
            instance.name = validated_data.get("name", instance.name)
            instance.status = validated_data.get("status", instance.status)
            instance.save()
            return instance
        except Exception as e:
            return e


class ZoneUpdateSerializer(serializers.ModelSerializer):
    name = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    countries_id = serializers.ListField(required=True)
    status = serializers.BooleanField(required=False)

    class Meta:
        model = Zone
        fields = ("id", "countries_id", "name", "status")

    def update(self, instance, validated_data):
        try:
            instance.name = validated_data.get("name", instance.name)
            instance.status = validated_data.get("status", instance.status)
            if "countries_id" in validated_data.keys():
                countries = validated_data.pop("countries_id")
                countries = list(set(countries))
                for each in ZoneCountries.objects.filter(
                    zone__id=instance.id, status=True
                ):
                    each.status = False
                    each.save()

                for each in countries:
                    zone_count = {}
                    zone_count["countries"] = Countries.objects.get(id=each)
                    zone_count["zone"] = Zone.objects.get(id=instance.id)
                    create = ZoneCountries.objects.create(**zone_count)
                    create.save()

            instance.save()
            return instance
        except Exception as e:
            return e
