import os
import django
from django.utils.text import slugify

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cspro.settings.settings")
django.setup()

import threading
from django.db import transaction
from api.models import Approach


def add_approches_thread():
	
	t1 = threading.Thread(target=add_approches())
	t1.start()

def add_approches():
	try:
		approches = [{"name":'[PERCEVAL] - Full sternotomy',"id":1},{"name":'[PERCEVAL] - Median/mini sternotomy',"id":2},{"name":'[PERCEVAL] - RAT',"id":3},{"name":'[SOLO SMART] - Full sternotomy',"id":4},{"name":'[SOLO SMART] - Median/mini sternotomy',"id":5},{"name":'[SOLO SMART] - RAT',"id":6},{"name":'[MEMO 3D RECHORD] - Full sternotomy',"id":7},{"name":'[MEMO 3D RECHORD] - RAT',"id":8},{"name":'[PERCEVAL] - Masterproctorship',"id":25},{"name":'NOT APPLICABLE',"id":26}]
		for each in approches:
			with transaction.atomic():
				x = Approach.objects.get_or_create(**each)
				if x[1] == False:
					print("Approach Already Exsist")
				else:
					print ("Approach are added successfully")
	except Exception as e:
		print(e)

if __name__ == "__main__":
	add_approches_thread()