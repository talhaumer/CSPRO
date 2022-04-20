import os

import django
from django.utils.text import slugify

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cspro.settings.settings")
django.setup()

import csv
import threading

from django.db import transaction

from api.models import Speciality


def add_speciality_thread():
    # data = Property.objects.all().update(canonical_link=None)

    t1 = threading.Thread(target=add_speciality())
    t1.start()


def add_speciality():
    try:
        specialities = [
            "Surgeon",
            "Anesthesiologist",
            "Nurses",
            "Perfusionist",
            "Corcym Employee",
            "Other",
        ]
        for speciality in specialities:
            with transaction.atomic():
                dic = {}
                dic["name"] = speciality
                x = Speciality.objects.get_or_create(**dic)
                if x[1] == False:
                    print("Speciality  Already Exsist")
                else:
                    print("Speciality  are added successfully")
    except Exception as e:
        print(e)


if __name__ == "__main__":
    add_speciality_thread()
