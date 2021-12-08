import os
import django
from django.utils.text import slugify

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cspro.settings.settings")
django.setup()

import threading
from django.db import transaction
from api.models import EventType
import csv


def add_focus_thread():
	# data = Property.objects.all().update(canonical_link=None)

	t1 = threading.Thread(target=add_focus())
	t1.start()

def add_focus():
	try:
		types = ['Speaking at corcym webinar (HCP virtual meetings)', 'Speaking at corcym webinar (HCP Peer-to-Peer event)', 'Speaking / Training at corcym event (Patient education program)', 'Speaking / Training at third party event (HCP education)', 'Speaking / Training at third party event (Patient education)', 'Speaking/Training at  Corcym Event-Symposium (At third party)']
		for each in types:
			with transaction.atomic():
				dic = {}
				dic['name'] = each
				x = EventType.objects.get_or_create(**dic)
				if x[1] == False:
					print("Event Type  Already Exsist")
				else:
					print ("Event Type  are added successfully")
	except Exception as e:
		print(e)

if __name__ == "__main__":
	add_focus_thread()