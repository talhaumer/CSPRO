import os

import django
from django.utils.text import slugify

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cspro.settings.settings")
django.setup()

import csv
import threading

from django.db import transaction

from api.models import Audience


def add_audience_thread():
    t1 = threading.Thread(target=add_audience())
    t1.start()


def add_audience():
    try:
        audience = [
            "Cardic Surgeons",
            "Perfusionist",
            "Cardiologists",
            "Anesthesialogists",
            "Nurses",
            "Others(please specify in notes)",
        ]
        for each in audience:
            with transaction.atomic():
                dic = {}
                dic["audience"] = each
                x = Audience.objects.get_or_create(**dic)
                if x[1] == False:
                    print("Audience Already Exsist")
                else:
                    print("Audience are added successfully")
    except Exception as e:
        print(e)


if __name__ == "__main__":
    add_audience_thread()
