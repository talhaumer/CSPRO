import os

import django
from django.utils.text import slugify

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cspro.settings.settings")
django.setup()

import csv
import threading

from django.db import transaction

from api.models import Hcp_role


def add_solution_thread():
    # data = Property.objects.all().update(canonical_link=None)

    t1 = threading.Thread(target=add_solution())
    t1.start()


def add_solution():
    try:
        role = [
            "Moderator",
            "Speaker",
            "Partecipant Advisory Board",
            "HCP Engaged no presentation required",
        ]
        for each in role:
            with transaction.atomic():
                dic = {}
                dic["name_of_role"] = each
                x = Hcp_role.objects.get_or_create(**dic)
                if x[1] == False:
                    print("speaker role  Already Exsist")
                else:
                    print("speaker role  are added successfully")
    except Exception as e:
        print(e)


if __name__ == "__main__":
    add_solution_thread()
