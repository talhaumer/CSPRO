
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cspro.settings.settings")
django.setup()


import threading
from django.db import transaction
from api.masterproctorship.models import MasterProctorShipConstantData


def add_data_thread():
	t1 = threading.Thread(target=add_data())
	t1.start()

def add_data():
	try:
		data = ['Certification Of a New Proctor', 'Advanced Training With a Masterproctor']
		for each in data:
			with transaction.atomic():
				data = {'name': each}
				x = MasterProctorShipConstantData.objects.get_or_create(**data)
				if x[1] == False:
					print("Master ProctorShip ConstantData  Already Exsist")
				else:
					print ("Master ProctorShip ConstantData  are added successfully")
	except Exception as e:
		print(e)

if __name__ == "__main__":
	add_data_thread()