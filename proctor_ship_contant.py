
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cspro.settings.settings")
django.setup()


import threading
from django.db import transaction
from api.proctorship.models import ConstantData


def add_data_thread():
	t1 = threading.Thread(target=add_data())
	t1.start()

def add_data():
	try:
		data = [{"name":"First training","type":"types-of-training","field":"dropdown"},{"name":"Advanced Training","type":"types-of-training","field":"dropdown"},{"name":"To open new center","type":"types-of-first-training","field":"dropdown"},{"name":"Center Already Open - New Surgeon","type":"types-of-first-training","field":"dropdown"},{"name":"First proctorship","type":"types-of-first-training","field":"radiobutton"},{"name":"Second implant","type":"types-of-first-training","field":"radiobutton"},{"name":"other-advanced-training","type":"types-of-advanced-training","field":"dropdown"},{"name":"Training after a complaint","type":"types-of-advanced-training","field":"dropdown"},{"name":"Follow-up proctorship after 10 cases","type":"types-of-advanced-training","field":"dropdown"},{"name":"The surgeon implants","type":"other-advanced-training","field":"dropdown"},{"name":"The surgeon does not implants regularly","type":"other-advanced-training","field":"dropdown"},{"name":"MICS: RAT","type":"other-advanced-training","field":"radiobutton"},{"name":"MICS MINISTERNOTOMY","type":"other-advanced-training","field":"dropdown"},{"name":"Surgeon","type":"title","field":"radiobutton"},{"name":"Anesthesiologist","type":"title","field":"dropdown"},{"name":"Nurse","type":"title","field":"dropdown"},{"name":"Perfusionist","type":"title","field":"dropdown"},{"name":"Other","type":"title","field":"dropdown"},{"name":"Full Sternotomy","type":"mvr/avr-approach","field":"dropdown"},{"name":"Median/mini strenotomy","type":"mvr/avr-approach","field":"dropdown"},{"name":"RAT","type":"mvr/avr-approach","field":"dropdown"}, {"name":"Failed Initial Experience", "type":"other-advanced-training", "field":"radiobutton"}, {"name":"Others", "type":"other-advanced-training", "field":"radiobutton"}, {"name":"Referral Issues", "type":"other-advanced-training", "field":"radiobutton"}]

		for each in data:
			with transaction.atomic():
				x = ConstantData.objects.get_or_create(**each)
				if x[1] == False:
					print(" ConstantData  Already Exsist")
				else:
					print ("ConstantData  are added successfully")

	except Exception as e:
		print(e)

if __name__ == "__main__":
	add_data_thread()