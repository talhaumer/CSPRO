import os
import django
from django.utils.text import slugify

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cspro.settings.settings")
django.setup()

import threading
from django.db import transaction
from api.models import Languages
import csv


def add_languages_thread():
	# data = Property.objects.all().update(canonical_link=None)

	t1 = threading.Thread(target=add_language())
	t1.start()

def add_language():
	try:
		languages = ['English', 'French', 'Italian', 'Arabic', 'Dutch','Deutsch', 'Greek', 'Spanish', 'japanese', 'Russian']
		for each in languages:
			with transaction.atomic():
				dic = {}
				dic['language'] = each
				x = Languages.objects.get_or_create(**dic)
				if x[1] == False:
					print("Languages  Already Exsist")
				else:
					print ("Languages  are added successfully")
	except Exception as e:
		print(e)

if __name__ == "__main__":
	add_languages_thread()