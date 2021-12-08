import os
import django
from django.utils.text import slugify

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cspro.settings.settings")
django.setup()
from django.contrib.staticfiles.storage import staticfiles_storage

import threading
from django.db import transaction
from api.models import AreaOfExperties
import csv


def add_experties_thread():
    # data = Property.objects.all().update(canonical_link=None)
    t1 = threading.Thread(target=experties())
    t1.start()

def experties():
    try:
        print("==========New Cron=============")
        # italy = pytz.timezone("Europe/Rome")
        # a = datetime.now(italy)
        # print(f'Current Time of itally : {a}')
        file_path = staticfiles_storage.path('experties.csv')
        with open(file_path) as csv_file:
            counntries = csv.reader(csv_file, delimiter=',')
            line_count = 0
            for row in counntries:
                if line_count == 0:
                    print(f'Column names are {", ".join(row)}')
                    line_count += 1
                else:
                    if get_or_create_experties(row):
                        print("Focus Saved Successfully")
                    else:
                        print("Focus Already Existed")
                    line_count += 1
    except Exception as e:
        print(f'Error : {e}')
        return e

def get_or_create_experties(data):
    """
    Get or create a Country Object
    :param country_data: Country attributes in DICT
    :return: Country Object
    """

    try:
        # print(country_data)
        area_experties = AreaOfExperties.objects.get(id=data[0])
        return False
    except AreaOfExperties.DoesNotExist:
        print("No Country Found")
        area_experties = AreaOfExperties(
            id =int(data[0]),
            name=data[1],
        )
        area_experties.save()
        return True


add_experties_thread()