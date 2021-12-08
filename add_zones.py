import json
import os
import django

from django.utils.text import slugify

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cspro.settings.settings")
django.setup()

import threading
import csv
from django.contrib.staticfiles.storage import staticfiles_storage
from django.db import transaction
from api.zone.models import Zone, ZoneCountries, Countries
from django.utils.text import slugify



def add_zones_thread():
    t1 = threading.Thread(target=zones())
    t1.start()

def zones():
    try:
        print("==========Add Zone=============")
        file_path = staticfiles_storage.path('zone.csv')
        with open(file_path) as csv_file:
            zone = csv.reader(csv_file, delimiter=',')
            line_count = 0
            for row in zone:
                if line_count == 0:
                    print(f'Column names are {", ".join(row)}')
                    line_count += 1
                else:
                    if get_or_create_country(row):
                        print("Zone Saved Successfully")
                    else:
                        print("Zone Already Existed")
                    line_count += 1
    except Exception as e:
        print(f'Error : {e}')
        return e

def get_or_create_country(zone_data):
    zone_name = zone_data[0]
    zone_countries = json.loads(zone_data[1])
    zone_id = zone_data[2]
    """
    Get or create a Country Object
    :param country_data: Country attributes in DICT
    :return: Country Object
    """

    try:
        # print(country_data)
        zone = Zone.objects.get(id=zone_id)
        return False
    except Zone.DoesNotExist:
        print("No Zone Found")
        with transaction.atomic():
            zone = Zone.objects.create(id = zone_id,name = zone_name)
            for each in zone_countries:
                zone_countries = ZoneCountries.objects.create(zone = zone,
                                             countries = Countries.objects.get(id = int(each)))

            zone.save()
            return True


add_zones_thread()