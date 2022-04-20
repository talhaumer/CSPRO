import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cspro.settings.settings")
django.setup()

import csv
import threading

from django.contrib.staticfiles.storage import staticfiles_storage

from api.zone.models import Countries


def add_countries_thread():
    t1 = threading.Thread(target=countries())
    t1.start()


def countries():
    try:
        file_path = staticfiles_storage.path("countries.csv")
        with open(file_path) as csv_file:
            counntries = csv.reader(csv_file, delimiter=",")
            line_count = 0
            for row in counntries:
                if line_count == 0:
                    print(f'Column names are {", ".join(row)}')
                    line_count += 1
                else:
                    if get_or_create_country(row):
                        print("Country Saved Successfully")
                    else:
                        print("Country Already Existed")
                    line_count += 1
    except Exception as e:
        print(f"Error : {e}")
        return e


def get_or_create_country(country_data):
    """
    Get or create a Country Object
    :param country_data: Country attributes in DICT
    :return: Country Object
    """

    try:
        country = Countries.objects.get(name__iexact=country_data[1].lower())
        return False
    except Countries.DoesNotExist:
        print("No Country Found")
        country = Countries(id=int(country_data[0]), name=country_data[1], status=True)
        country.save()
        return True


add_countries_thread()
