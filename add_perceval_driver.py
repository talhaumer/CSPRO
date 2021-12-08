
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cspro.settings.settings")
django.setup()


import threading
from django.db import transaction
from api.feedback.models import PercevelDriver


def add_data_thread():
	t1 = threading.Thread(target=add_data())
	t1.start()

def add_data():
	try:
		data = ['--MICS','--Complex','--Combined','--Redo','--Others','--Easy of use during preparation','--Easy of use during implantation','Short cross clamp time and CPB time/speed of implantation','Good hemodynamics','durability','--Advantages VS TAVI','--Advantages VS SAVR','--Features for VinV','--Trainee left it blank']
		for each in data:
			with transaction.atomic():
				data = {'name': each}
				x = PercevelDriver.objects.get_or_create(**data)
				if x[1] == False:
					print("PercevelDriver Already Exsist")
				else:
					print ("PercevelDriver are added successfully")
	except Exception as e:
		print(e)

if __name__ == "__main__":
	add_data_thread()