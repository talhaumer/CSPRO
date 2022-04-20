import json
import os
from datetime import datetime

import django
from django.utils.text import slugify

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cspro.settings.settings")
django.setup()

import csv
import threading

from django.contrib.staticfiles.storage import staticfiles_storage
from django.db import transaction
from django.utils.text import slugify

from api.models import Hospital, Languages
from api.proctors.models import Proctors, ProctorsHospital
from api.users.models import Role, User
from api.zone.models import Countries


def add_proctors_thread():
    t1 = threading.Thread(target=proctors())
    t1.start()


def proctors():
    try:
        print("==========Add Hospitals=============")
        file_path = staticfiles_storage.path("proctors.csv")
        with open(file_path, errors="replace") as csv_file:
            zone = csv.reader(csv_file, delimiter=",")
            line_count = 0
            for row in zone:
                if line_count == 0:
                    print(f'Column names are {", ".join(row)}')
                    line_count += 1
                else:
                    if get_or_create_proctors(row):
                        print("Proctors Saved Successfully")
                    else:
                        print("Proctors Already Existed")

                    line_count += 1
    except Exception as e:
        print(f"Error : {e}")
        return e


def get_or_create_proctors(data):
    try:
        name = str(data[0])
        print("---------------------------Name", ":", name)
        email = str(data[1])
        is_active = True
        if int(data[2]) == 0:
            is_active = False

        image = str(data[3])
        country = int(data[4])
        role = Role.objects.get(code="proctor")
        area_of_experties = []
        if str(data[5]) != "NULL":
            area_of_experties = json.loads(data[5])

        spoken_languages = json.loads(data[7])
        approach = json.loads(data[8])
        products = json.loads(data[10])

        telephone = str(data[6])
        publication = str(data[9])
        note = str(data[11])

        only_speaker = True
        if int(data[12]) == 0:
            only_speaker = False

        contract_starting_details = None
        if str(data[13]) != "NULL":
            contract_starting_details = datetime.strptime(str(data[13]), "%m/%d/%Y")

        contract_ending_details = None
        if str(data[14]) != "NULL":
            contract_ending_details = datetime.strptime(str(data[14]), "%m/%d/%Y")
        resume = str(data[15])

        proctorShip_contract_start_details = None
        if str(data[16]) != "NULL":
            proctorShip_contract_start_details = datetime.strptime(
                str(data[16]), "%m/%d/%Y"
            )

        proctorShip_contract_ending_details = None
        if str(data[17]) != "NULL":
            proctorShip_contract_ending_details = datetime.strptime(
                str(data[17]), "%m/%d/%Y"
            )

        unavailability_start_date = None
        if str(data[18]) != "NULL":
            unavailability_start_date = datetime.strptime(str(data[18]), "%m/%d/%Y")

        unavailability_end_date = None
        if str(data[19]) != "NULL":
            unavailability_end_date = datetime.strptime(str(data[19]), "%m/%d/%Y")

        reason = str(data[20])

        is_masterproctorship = True
        if str(data[21]) == "FALSE":
            is_masterproctorship = False
        hospital = int(data[22])

        proctor_id = int(data[23])

        with transaction.atomic():
            user = User.objects.create(
                **{
                    "name": name,
                    "is_active": is_active,
                    "email": email,
                    "image": image,
                    "role": role,
                    "country": Countries.objects.get(id=country),
                }
            )

            proctors = Proctors.objects.create(
                **{
                    "id": proctor_id,
                    "user": user,
                    "telephone": telephone,
                    "publication": publication,
                    "note": note,
                    "only_speaker": only_speaker,
                    "contract_starting_details": contract_starting_details,
                    "contract_ending_details": contract_ending_details,
                    "resume": resume,
                    "proctorShip_contract_start_details": proctorShip_contract_start_details,
                    "proctorShip_contract_ending_details": proctorShip_contract_ending_details,
                    "unavailability_start_date": unavailability_start_date,
                    "unavailability_end_date": unavailability_end_date,
                    "is_masterproctorship": is_masterproctorship,
                    "reason_why": reason,
                }
            )

            proctors.area_of_experties.add(*area_of_experties)
            for each in spoken_languages:
                proctors.spoken_languages.add(Languages.objects.get(code=str(each)))

            proctors.approach.add(*approach)
            proctors.products.add(*products)

            ProctorsHospital.objects.create(
                **{"proctors": proctors, "hospital": Hospital.objects.get(id=hospital)}
            )

            user.save()
            return True
    except Exception as e:
        print(str(e))


add_proctors_thread()
