import os
import django
from django.utils.text import slugify

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cspro.settings.settings")
django.setup()

import threading
from django.db import transaction
from api.models import Region
import csv


def add_region_thread():

	t1 = threading.Thread(target=add_region())
	t1.start()

def add_region():
	try:
		region = ['Europe', 'Latam', 'Canada', 'Meca', 'US','EUA', 'ANZ', 'Japan', 'China', 'Germany/ Switzerland/ Austria', 'South & East Asia', 'North America']
		for each in region:
			with transaction.atomic():
				dic = {}
				dic['region'] = each
				x = Region.objects.get_or_create(**dic)
				if x[1] == False:
					print("Region  Already Exsist")
				else:
					print ("Region  are added successfully")
	except Exception as e:
		print(e)

if __name__ == "__main__":
	add_region_thread()