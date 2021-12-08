
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cspro.settings.settings")
django.setup()
import threading
from django.db import transaction
from api.zone.models import Zone, Countries, ZoneCountries




def add_data_thread():
	t1 = threading.Thread(target=add_data())
	t1.start()

def add_data():
	try:
		with transaction.atomic():
			x = Zone.objects.get_or_create(name = 'world')
			if x[1] == False:
				print("World Zone Already Exsist")
			else:
				for each in Countries.objects.all():
					ZoneCountries.objects.create(zone = x[0],
												 countries=each)
				print("Zone Added")
	except Exception as e:
		print(e)

if __name__ == "__main__":
	add_data_thread()