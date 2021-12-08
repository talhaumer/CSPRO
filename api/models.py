from django.db import models
from api.zone.models import Zone, Countries
from main.models import Base
from django.utils.text import slugify
from model_utils import Choices

# Create your models here.

# focus and area of experties are same thing 
class AreaOfExperties(Base):
	name = models.CharField(max_length = 255, default= "", db_column= "AreaOfExpertiesName")
	code = models.SlugField(db_column = 'Code', default = "")

	class Meta:
		db_table = 'AreaOfExperties'


	def __str__(self):
		return self.name

	def save(self, *args, **kwargs):
		try:
			if not self.pk:
				self.code = slugify(self.name)
			super().save()
		except Exception:
			raise


class Approach(Base):
	name = models.CharField(max_length = 255, default= "", db_column= "ApproachName")
	code = models.SlugField(db_column = 'Code', default = "")

	class Meta:
		db_table = 'Approach'


	def __str__(self):
		return self.name

	def save(self, *args, **kwargs):
		try:
			if not self.pk:
				self.code = slugify(self.name)
			super().save()
		except Exception:
			raise

			

class Languages(Base):
	language = models.CharField(max_length = 50, null =True, blank = True)
	code = models.SlugField(db_column='Code', default='')

	class Meta:
		db_table = 'Languages'

	def save(self, *args, **kwargs):
		try:
			if not self.pk:
				self.code = slugify(self.language)
			super().save()
		except Exception:
			raise

	def __str__(self):
		return self.language


################################## Products ##################################
class Products(Base):
	product_name = models.CharField(max_length= 200)
	# product_typology = models.CharField(max_length = 150)
	# product_type = models.CharField(max_length = 50)
	image = models.ImageField(upload_to="", default="")
	code = models.SlugField(db_column='Code', default='')

	class Meta:
		db_table = 'Products'

	def save(self, *args, **kwargs):
		try:
			if not self.pk:
				self.code = slugify(self.product_name)
			super().save()
		except Exception:
			raise

	def __str__(self):
		return self.product_name

################################## Hospital ##################################
class Hospital(Base):
	hospital_name = models.CharField(max_length = 255, db_column="HospitalName", blank=True, null=True)
	number_of_trainee = models.IntegerField(default=0, null = False,  blank = False)
	products = models.ManyToManyField(Products, related_name = 'hospitals_products', db_column= "HospitalProducts", blank = True)
	location = models.CharField(max_length = 255, default="", db_column = "Location")
	is_it_preceptorship = models.BooleanField(default = False, db_column = 'IsItPreceptorship')
	qualified_for_news_mics_program = models.BooleanField(default = False, db_column = 'QualifiedForNewsMicsProgram')
	cognos_id  = models.CharField(default= '', db_column= "CognosID", max_length = 255, blank = True, null = True)
	code = models.SlugField(db_column='Code', default='', max_length = 255)
	deleted = models.BooleanField(db_column = 'Deleted', default = False)


	class Meta:
		db_table = 'Hospital'

	def __str__(self):
		return self.hospital_name

	def save(self, *args, **kwargs):
		try:
			if not self.pk:
				self.code = slugify(self.hospital_name)
			super().save()
		except Exception:
			raise

class HospitalCountires(Base):
	country = models.ForeignKey(Countries, null=True, blank=True, db_column="HospitalCountry",
								related_name="hospital_country", on_delete=models.CASCADE)
	hospital = models.ForeignKey(Hospital, null=True, blank=True, db_column="HospitalId",
								related_name="hospital_id", on_delete=models.CASCADE)
	class Meta:
		db_table = "HospitalCountires"



class Hcp_role(Base):
	name_of_role = models.CharField(max_length= 255)
	code  = models.CharField(max_length=255, default='')

	class Meta:
		db_table  = 'Hcp_role'

	def __str__(self):
		return self.code

	def save(self, *args, **kwargs):
		try:
			if not self.pk:
				self.code = slugify(self.name_of_role)
			super().save()
		except Exception:
			raise



class Solution(Base):
	solution = models.CharField(max_length = 50, null= True, blank = True)
	class Meta:
		db_table = 'Solution'

	def __str__(self):
		return self.solution

class Audience(Base):
	audience = models.CharField(max_length= 50, null= True, blank = True)
	class Meta:
		db_table = 'Audience'

	def __str__(self):
		return self.audience

class Region(Base):
	region = models.CharField(max_length= 50, null = True, blank= True)
	
	class Meta:
		db_table = 'Region'

	def __str__(self):
		return self.region


class EventType(Base):
	name = models.CharField(max_length = 255, default= "", db_column= "AreaOfExpertiesName")
	code = models.SlugField(db_column = 'Code', default = "", max_length=255)

	class Meta:
		db_table = 'EventType'


	def __str__(self):
		return self.name

	def save(self, *args, **kwargs):
		try:
			if not self.pk:
				self.code = slugify(self.name)
			super().save()
		except Exception:
			raise





class Speciality(Base):
	name = models.CharField(max_length = 255, default= "", db_column= "AreaOfExpertiesName")
	code = models.SlugField(db_column = 'Code', default = "")

	class Meta:
		db_table = 'Speciality'


	def __str__(self):
		return self.code

	def save(self, *args, **kwargs):
		try:
			if not self.pk:
				self.code = slugify(self.name)
			super().save()
		except Exception:
			raise


ORDER_COLUMN_CHOICES = Choices(
	('0', 'id'),
	('1', 'hospital_name'),
	('2', 'number_of_trainee'),
	('3', 'location'),
	('4', 'cognos_id'),
)

def query_hospital_by_args(query_object, **kwargs):
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

		queryset = Hospital.objects.filter(query_object)
		print("----------------------------")
		print(queryset)
		
		total = queryset.count()
		if search_value:
			queryset = queryset.filter(Q(id__icontains=search_value) |
											Q(hospital_name__icontains=search_value) |
											Q(number_of_trainee__icontains=search_value) |
											Q(location__icontains=search_value) |
											Q(cognos_id__icontains=search_value))

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