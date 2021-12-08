from django.db import models
from main.models import Base
from api.models import Languages, AreaOfExperties, Approach, Products, Hospital
from api.zone.models import Countries
from model_utils import Choices
from api.users.models import User
# Create your models here.
class Proctors(Base):
	user = models.ForeignKey(User, db_column = "UserId" ,default = None, related_name = "proctor_user",on_delete= models.CASCADE)
	area_of_experties = models.ManyToManyField(AreaOfExperties, related_name = "proctors_area_of_experties",db_column= "AreaOfExpertiesId")
	telephone = models.CharField(max_length = 25)
	spoken_languages = models.ManyToManyField(Languages, db_column = "ProctorsLanguageID", related_name = "proctors_spoken_language")
	approach = models.ManyToManyField(Approach, db_column = "ProctorsApproachID", related_name = "proctors_approach") 
	publication = models.TextField(db_column = "Publications")
	products = models.ManyToManyField(Products, related_name = 'proctors_products', db_column= "ProctorsProductsID")
	note = models.TextField(db_column  = "Note")
	Only_Speaker = (
		(True, 'Yes'),
		(False, 'No'),
		)
	only_speaker = models.BooleanField(default = False, db_column = "OnlySpeaker")
	contract_starting_details = models.DateField(db_column  = 'ContractStartingDetails')
	contract_ending_details = models.DateField(db_column = 'ContractEndingDetails')
	resume= models.FileField(upload_to ='uploads/', db_column = "Resume", null = True, blank = True)
	proctorShip_contract_start_details = models.DateField(db_column  = 'ProctorShipContractStartingDetails', null = True, blank = True)
	proctorShip_contract_ending_details = models.DateField(db_column  = 'ProctorShipContractEndingDetails', null = True, blank = True)
	unavailability_start_date = models.DateField(db_column  = 'UnavailabilityStartDate', null = True, blank = True)
	unavailability_end_date = models.DateField(db_column  = 'UnavailabilityEndDate', null = True, blank = True)
	reason_why = models.TextField(db_column ="ReasonWhy", blank = True, null = True)
	IS_MASTERPROCTORSHIP = (
		(True, 'Yes'),
		(False, 'No'),
		)
	is_masterproctorship = models.BooleanField(default = False, db_column = "IsMasterProctorShip")


	class Meta:
		db_table = 'Proctors'



class ProctorsHospital(Base):
	proctors = models.ForeignKey(Proctors, on_delete=models.CASCADE, db_column='ProctorsId', related_name='proctors_pivot_id', null = True, default=None)
	hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE, db_column='HospitalId', related_name='hospital_pivot_id', null = True, default=None)
	status = models.BooleanField(default=True, db_column='ProctorsHospitalStatus')
	class Meta:
		db_table = 'ProctorsHospital'


ORDER_COLUMN_CHOICES = Choices(
	('0', 'id'),
	('1', 'name'),
	('2', 'email'),
	('3', 'telephone'),
)

def query_proctors_by_args(query_object, **kwargs):
	try:
		draw = int(kwargs.get('draw', None)[0])
		length = int(kwargs.get('length', None)[0])
		start = int(kwargs.get('start', None)[0])
		search_value = kwargs.get('search[value]', None)[0]
		order_column = kwargs.get('order[0][column]', None)[0]
		order = kwargs.get('order[0][dir]', None)[0]
		order_column = ORDER_COLUMN_CHOICES[order_column]

		# django orm '-' -> desc
		if order == 'desc':
			order_column = '-' + order_column

		queryset = Proctors.objects.filter(query_object)
		print("----------------------------")
		print(queryset)
		
		total = queryset.count()
		if search_value:
			queryset = queryset.filter(Q(id__icontains=search_value) |
											Q(name__icontains=search_value) |
											Q(email__icontains=search_value) |
											Q(telephone__icontains=search_value))

		count = queryset.count()
		queryset = queryset.order_by(order_column)[start:start + length]
		return {
			'items': queryset,
			'count': count,
			'total': total,
			'draw': draw
		}
	except Exception as e:
		print(e)		
		return None

