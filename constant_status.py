import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cspro.settings.settings")
django.setup()


import threading

from django.db import transaction

from api.status.models import StatusConstantData


def add_data_thread():
    t1 = threading.Thread(target=add_data())
    t1.start()


def add_data():
    try:
        data = [
            "Pending",
            "Processing",
            "Alternative Proposal",
            "Confirmed",
            "Cancelled",
            "Closed",
            "Past Due",
            "Waiting For Docs",
        ]
        for each in data:
            with transaction.atomic():
                data = {"name": each}
                x = StatusConstantData.objects.get_or_create(**data)
                if x[1] == False:
                    print("Status Constant Data Already Exsist")
                else:
                    print("Status Constant Data are added successfully")
    except Exception as e:
        print(e)


if __name__ == "__main__":
    add_data_thread()
