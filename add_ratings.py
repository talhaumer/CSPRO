
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cspro.settings.settings")
django.setup()


import threading
from django.db import transaction
from api.feedback.models import Rating


def add_data_thread():
	t1 = threading.Thread(target=add_data())
	t1.start()

def add_data():
	try:
		data = ['Poor', 'Average', 'Good', 'Excellent']
		for each in data:
			with transaction.atomic():
				data = {'name': each}
				x = Rating.objects.get_or_create(**data)
				if x[1] == False:
					print("Rating Already Exsist")
				else:
					print ("Rating are added successfully")
	except Exception as e:
		print(e)

if __name__ == "__main__":
	add_data_thread()