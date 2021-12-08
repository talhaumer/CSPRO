
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cspro.settings.settings")
django.setup()


import threading
from django.db import transaction
from api.models import Products


def add_data_thread():
	t1 = threading.Thread(target=add_data())
	t1.start()

def add_data():
	try:

		data =  [{"image":"media/uploads/perceval_PkRWbdD.jpg","product_name":"Perceval", "id":2},{"image":"media/uploads/solo_smart_hIhjM0t.jpg","product_name":"Solo Smart", "id":3},{"image":"media/uploads/memo-1_bpjJwuz.jpg","product_name":"Memo Family", "id":1}]
		for each in data:
			with transaction.atomic():
				x = Products.objects.get_or_create(**each)
				if x[1] == False:
					print("Products Already Exsist")
				else:
					print ("Products are added successfully")
	except Exception as e:
		print(e)

if __name__ == "__main__":
	add_data_thread()