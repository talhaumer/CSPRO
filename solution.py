import os
import django
from django.utils.text import slugify

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cspro.settings.settings")
django.setup()

import threading
from django.db import transaction
from api.models import Solution
import csv


def add_solution_thread():
	# data = Property.objects.all().update(canonical_link=None)

	t1 = threading.Thread(target=add_solution())
	t1.start()

def add_solution():
	try:
		solution = ['Aortic Perceval', 'Aortic Crown', 'Mitral Memo Family']
		for each in solution:
			with transaction.atomic():
				dic = {}
				dic['solution'] = each
				x = Solution.objects.get_or_create(**dic)
				if x[1] == False:
					print("Solution  Already Exsist")
				else:
					print ("Solution  are added successfully")
	except Exception as e:
		print(e)

if __name__ == "__main__":
	add_solution_thread()