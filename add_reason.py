
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cspro.settings.settings")
django.setup()


import threading
from django.db import transaction
from api.feedback.models import Reason


def add_data_thread():
	t1 = threading.Thread(target=add_data())
	t1.start()

def add_data():
	try:
		data = ['The number of patients implanted is equal then number of patients selected', 'The patient was not operated at all', 'Perceval could not be used-Upredicted bicuspid valve type 0', 'Annulus too small', 'Annulus too large', 'Other']
		for each in data:
			with transaction.atomic():
				data = {'name': each}
				x = Reason.objects.get_or_create(**data)
				if x[1] == False:
					print("Reason Already Exsist")
				else:
					print ("Reason are added successfully")
	except Exception as e:
		print(e)

if __name__ == "__main__":
	add_data_thread()