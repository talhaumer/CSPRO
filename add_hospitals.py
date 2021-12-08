from datetime import datetime
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
from api.zone.models import Countries
from api.models import Hospital, HospitalCountires

from django.utils.text import slugify



def add_hospitals_thread():
    t1 = threading.Thread(target=hospitals())
    t1.start()

def hospitals():
    try:
        print("==========Add Hospitals=============")
        file_path = staticfiles_storage.path('hospital.csv')
        with open(file_path) as csv_file:
            zone = csv.reader(csv_file, delimiter=',')
            line_count = 0
            for row in zone:
                if line_count == 0:
                    print(f'Column names are {", ".join(row)}')
                    line_count += 1
                else:
                    if get_or_create_country(row):
                        print("hospitals Saved Successfully")
                    else:
                        print("hospitals Already Existed")
                    line_count += 1
    except Exception as e:
        print(f'Error : {e}')
        return e

def get_or_create_country(data):
    try:
        hospital = Hospital.objects.get(id = int(data[9]))
        return False
    except Hospital.DoesNotExist:
        hospital_name = str(data[0])
        print(hospital_name)
        number_of_trainee = int(data[1])
        location = str(data[4])
        is_it_preceptorship = True
        if int(data[5]) == 0:
            is_it_preceptorship = False



        qualified_for_news_mics_program = True
        if int(data[6]) == 0:
            qualified_for_news_mics_program = False


        cognos_id = data[7]

        deleted = True
        if int(data[8]) == 0:
            deleted = False

        products = json.loads(data[2])

        country = int(data[3])
        hospital_id = int(data[9])
        print(is_it_preceptorship, qualified_for_news_mics_program, deleted)

        with transaction.atomic():
            hospitals = Hospital.objects.create(**{"id":hospital_id,"hospital_name":hospital_name,"number_of_trainee":number_of_trainee,"location":location,"is_it_preceptorship":is_it_preceptorship,"qualified_for_news_mics_program":qualified_for_news_mics_program,"cognos_id":cognos_id,"deleted":deleted})

            hospitals.products.add(*products)
            try:
                obj = {}
                obj['country'] = Countries.objects.get(id=country)
                obj['hospital'] = hospitals
                HospitalCountires.objects.create(**obj)
            except:
                pass
            hospitals.save()
            return True
    except:
        return False



add_hospitals_thread()