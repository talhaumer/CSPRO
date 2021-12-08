from rest_framework import serializers
from api.proctors.models import Proctors, ProctorsHospital
from api.models import Products, AreaOfExperties, Approach, Languages, Hospital
from api.zone.models import Countries
import json 
from api.users.models import User, Role
from django.db import transaction


class ChoiceField(serializers.ChoiceField):

	def to_representation(self, obj):
		if obj == '' and self.allow_blank:
			return obj
		return self._choices[obj]

	def to_internal_value(self, data):
		# To support inserts with the value
		if data == '' and self.allow_blank:
			return ''

		for key, val in self._choices.items():
			if val == data:
				return key
		self.fail('invalid_choice', input=data)

class ProctorsViewSerializer(serializers.ModelSerializer):
	proctor_name = serializers.SerializerMethodField(read_only = True)
	proctor_image = serializers.SerializerMethodField(read_only= True)
	proctor_email = serializers.SerializerMethodField(read_only = True)
	country = serializers.SerializerMethodField(read_only = True)
	hospital = serializers.SerializerMethodField(read_only = True)
	area_of_experties = serializers.StringRelatedField(read_only = True, many = True) 
	telephone = serializers.CharField(read_only = True)
	spoken_languages = serializers.StringRelatedField(read_only = True, many = True)
	approach = serializers.StringRelatedField(read_only = True, many = True) 
	publication = serializers.CharField(read_only = True)
	products = serializers.StringRelatedField(read_only = True, many = True)
	note = serializers.CharField(read_only = True)
	only_speaker = serializers.BooleanField(read_only = True)
	contract_starting_details = serializers.DateField(read_only = True)
	contract_ending_details = serializers.DateField(read_only = True)
	resume = serializers.FileField(read_only = True)
	proctorShip_contract_start_details = serializers.DateField(read_only = True)
	proctorShip_contract_ending_details = serializers.DateField(read_only = True)
	unavailability_start_date = serializers.DateField(read_only = True)
	unavailability_end_date = serializers.DateField(read_only = True)
	reason_why = serializers.CharField(read_only = True)
	is_masterproctorship = serializers.BooleanField(read_only = True)
	is_active = serializers.SerializerMethodField(read_only=True)
	
	class Meta:
		model = Proctors
		fields = "__all__"

	def get_is_active(self, obj):
		return obj.user.is_active

	def get_proctor_name(self, obj):
		return obj.user.name

	def get_proctor_email(self, obj):
		return obj.user.email

	def get_country(self, obj):
		try:
			return obj.user.country.name
		except:
			return ''
	def get_hospital(self, obj):
		try:
			return obj.proctors_pivot_id.get(status = True).hospital.hospital_name
		except:
			return None

	def get_area_of_experties(self, obj):
		try:
			return obj.area_of_experties.name
		except:
			return ''

	def get_spoken_languages(self, obj):
		try:
			return obj.spoken_languages.language
		except:
			return ''

	def get_approach(self, obj):
		try:
			return obj.approach.name
		except:
			return ''

	def get_products(self, obj):
		try:
			return obj.products.product_name
		except:
			return ''

	def get_proctor_image(self, obj):
		try:
			return obj.user.image.url
		except:
			return None


class ProctorsSerializer(serializers.ModelSerializer):
	# country = serializers.SerializerMethodField(read_only = True)
	telephone = serializers.CharField(write_only = True)
	publication = serializers.CharField(write_only = True, allow_blank = True, allow_null = True)
	note = serializers.CharField(write_only = True, allow_blank = True, allow_null = True)
	only_speaker = serializers.BooleanField( write_only= True)
	contract_starting_details = serializers.DateField(write_only = True)
	contract_ending_details = serializers.DateField(write_only = True)
	resume= serializers.FileField(write_only = True)
	proctorShip_contract_start_details = serializers.DateField(write_only = True, allow_null = True)
	proctorShip_contract_ending_details = serializers.DateField(write_only = True,  allow_null = True)
	unavailability_start_date = serializers.DateField(write_only = True,  allow_null = True)
	unavailability_end_date = serializers.DateField(write_only = True, allow_null = True)
	reason_why = serializers.CharField(write_only = True, allow_blank = True, allow_null = True)
	hospital_id = serializers.IntegerField(write_only  = True)
	country_id = serializers.IntegerField(write_only= True)
	products_id = serializers.CharField(write_only = True, allow_null= True, allow_blank = True)
	area_of_experties_id = serializers.CharField(write_only = True,allow_null= True, allow_blank = True)
	approach_id = serializers.CharField(write_only = True,allow_null= True, allow_blank = True)
	spoken_languages_id = serializers.CharField(write_only = True, allow_null= True, allow_blank = True)
	is_masterproctorship = serializers.BooleanField( write_only = True)
	# name = serializers.CharField(required = True)
	is_active = serializers.BooleanField(write_only = True)
	email = serializers.EmailField(write_only = True)
	image = serializers.ImageField(write_only = True, allow_null=True)
	# proctor_info = serializers.SerializerMethodField(read_only = True)
	
	class Meta:
		model = User
		fields = ['id','telephone', 'publication',  'note', 'only_speaker', 'contract_starting_details', 'contract_ending_details', 'resume', 'proctorShip_contract_start_details', 'proctorShip_contract_ending_details', 'unavailability_start_date', 'unavailability_end_date', 'reason_why', 'hospital_id', 'country_id', 'products_id', 'approach_id', 'is_masterproctorship', 'name', 'is_active','email','image', 'area_of_experties_id', 'spoken_languages_id' ]

	def string_to_list(self, data):
		if data != "":
			a_list = data.split(',')
			map_object = map(int, a_list)
			list_of_integers = list(map_object)
			print(list_of_integers)
			return list_of_integers

	def create(self, validated_data):
		try:
			with transaction.atomic():
				proctor_data = {'telephone':validated_data.pop("telephone"),'publication':validated_data.pop("publication"),'note':validated_data.pop("note"),'only_speaker':validated_data.pop("only_speaker"),'contract_starting_details':validated_data.pop("contract_starting_details"),'contract_ending_details':validated_data.pop("contract_ending_details"),'resume':validated_data.pop("resume"),'proctorShip_contract_start_details':validated_data.pop("proctorShip_contract_start_details"),'proctorShip_contract_ending_details':validated_data.pop("proctorShip_contract_ending_details"),'unavailability_start_date':validated_data.pop("unavailability_start_date"),'unavailability_end_date':validated_data.pop("unavailability_end_date"),'reason_why':validated_data.pop("reason_why"),'is_masterproctorship':validated_data.pop("is_masterproctorship")}
				hospital = validated_data.pop('hospital_id')
				y = self.string_to_list(validated_data.pop('approach_id'))
				z = self.string_to_list(validated_data.pop('area_of_experties_id'))
				l = self.string_to_list(validated_data.pop('spoken_languages_id'))
				x = self.string_to_list(validated_data.pop('products_id'))

				validated_data['role'] = Role.objects.get(code = 'proctor')
				user = User.objects.create(**validated_data)
				user.save()
				proctor_data['user'] = user
				proctor = Proctors.objects.create(**proctor_data)
				proctor_hospital = {
					"proctors" : proctor,
					"hospital" : Hospital.objects.get(id=hospital)
				}
				procotor_hospitals = ProctorsHospital.objects.create(**proctor_hospital)

				if y:
					proctor.approach.add(*y)
				if z:
					proctor.area_of_experties.add(*z)
				if l:
					proctor.spoken_languages.add(*l)
				if x:
					proctor.products.add(*x)

				return user
		except Exception as e:
			return  e

	# def get_proctor_info(self,obj):
	# 	try:
	# 		data = ProctorsViewSerializer(obj.proctor_user.all()).data
	# 		return  data
	# 	except:
	# 		return ''

	# def get_country(self, obj):
	# 	try:
	# 		return obj.country.name
	# 	except:
	# 		return ''


	# # def update(self, instance, validated_data):
	# 	x = validated_data.pop('products_id')
	# 	y = validated_data.pop('approach_id')
	# 	z = validated_data.pop('area_of_experties_id')
	# 	l = validated_data.pop('spoken_languages_id')

	# 	instance.name = validated_data.get('name', instance.name)
	# 	instance.hospital = validated_data.get('hospital', instance.hospital)
	# 	instance.products.clear()
	# 	instance.products.add(*x)
	# 	proctor.approach.add(*y)
	# 	proctor.area_of_experties.add(*z)
	# 	proctor.spoken_languages.add(*l)

	# 	instance.save()
	# 	return instance



class ProctorsUpdateSerializer(serializers.ModelSerializer):
	name = serializers.CharField(required = False)
	email = serializers.EmailField(required = False)
	country = serializers.SerializerMethodField(read_only=True)
	hospital = serializers.SerializerMethodField(read_only=True)
	area_of_experties = serializers.SerializerMethodField(read_only=True)
	telephone = serializers.CharField(required = False)
	spoken_languages = serializers.SerializerMethodField(read_only=True)
	approach = serializers.SerializerMethodField(read_only=True)
	publication = serializers.CharField(required = False, allow_null=True, allow_blank=True)
	products = serializers.PrimaryKeyRelatedField(many = True, read_only = True)
	address = serializers.CharField(required = False)
	note = serializers.CharField(required = False, allow_blank=True, allow_null=True)
	only_speaker = serializers.BooleanField(required= False)
	contract_starting_details = serializers.DateField(required = False)
	contract_ending_details = serializers.DateField(required = False)
	resume= serializers.FileField(required = False)
	proctorShip_contract_start_details = serializers.DateField(required = False, allow_null=True)
	proctorShip_contract_ending_details = serializers.DateField(required = False, allow_null=True)
	unavailability_start_date = serializers.DateField(required = False, allow_null=True)
	unavailability_end_date = serializers.DateField(required = False, allow_null=True)
	reason_why = serializers.CharField(required = False, allow_null=True, allow_blank=True)
	hospital_id = serializers.CharField(required = False)
	country_id = serializers.CharField(required = False)
	approach_id = serializers.CharField(required = False)
	area_of_experties_id = serializers.CharField(required = False)
	products_id = serializers.CharField(write_only = False)
	spoken_languages_id = serializers.CharField(required = False)
	image = serializers.FileField(required = False)
	is_active = serializers.BooleanField(required = False)
	is_masterproctorship = serializers.BooleanField(required=False)

	class Meta:
		model = Proctors
		fields = "__all__"

	def string_to_list(self, data):
		if data != "":
			a_list = data.split(',')
			map_object = map(int, a_list)
			list_of_integers = list(map_object)
			print(list_of_integers)
			return list_of_integers


	def update(self, instance, validated_data):
		user_data = {
		"name":validated_data.pop('name'),
		"email":validated_data.pop('email'),
		"is_active":validated_data.pop('is_active'),
		"role":4
		}

		user_instance = User.objects.get(pk=instance.user.id)
		if "country_id" in validated_data.keys():
			validated_data['country'] = Countries.objects.get(pk = int(validated_data.pop('country_id')))
			user_instance.country = validated_data.get('country', user_instance.country)
			user_instance.save()
		
		if 'image' in validated_data.keys():
			user_instance.image = validated_data.get('image', user_instance.image)
			user_instance.save()

		User.objects.filter(id=instance.user.id).update(**user_data)
		instance.telephone = validated_data.get('telephone', instance.telephone)
		instance.publication  = validated_data.get('publication', instance.publication)
		instance.note = validated_data.get('note', instance.note)
		instance.only_speaker =validated_data.get('only_speaker', instance.only_speaker)
		instance.contract_starting_details = validated_data.get('contract_starting_details',instance.contract_starting_details)
		instance.contract_ending_details = validated_data.get('contract_ending_details', instance.contract_ending_details)
		if "resume" in validated_data.keys():
			instance.resume= validated_data.get('resume', instance.resume)
		instance.proctorShip_contract_start_details = validated_data.get('proctorShip_contract_start_details', instance.proctorShip_contract_start_details)
		instance.proctorShip_contract_ending_details = validated_data.get('proctorShip_contract_ending_details', instance.proctorShip_contract_ending_details)
		instance.unavailability_start_date = validated_data.get('unavailability_start_date', instance.unavailability_start_date)
		instance.unavailability_end_date = validated_data.get('unavailability_end_date',instance.unavailability_end_date)
		instance.reason_why = validated_data.get('reason_why', instance.reason_why)
		if 'hospital_id' in validated_data.keys():
			hospital = Hospital.objects.get(pk = validated_data.pop('hospital_id'))
			proctors_hospital = ProctorsHospital.objects.get(proctors__id=instance.id)
			proctors_hospital.status = False
			proctors_hospital.save()
			new_hospital = ProctorsHospital.objects.create(proctors = instance, hospital = hospital, status = True)
			new_hospital.save()
		instance.is_masterproctorship = validated_data.get('is_masterproctorship', instance.is_masterproctorship)

		y = self.string_to_list(validated_data.pop('approach_id'))
		z = self.string_to_list(validated_data.pop('area_of_experties_id'))
		l = self.string_to_list(validated_data.pop('spoken_languages_id'))
		x = self.string_to_list(validated_data.pop('products_id'))

		if y:
			instance.approach.clear()
			instance.approach.add(*y)
		if z:
			instance.area_of_experties.clear()
			instance.area_of_experties.add(*z)
		if l:
			instance.spoken_languages.clear()
			instance.spoken_languages.add(*l)
		if x:
			instance.products.clear()
			instance.products.add(*x)

		instance.save()
		return instance

	def get_country(self, obj):
		try:
			return obj.country.id
		except:
			return ''


	def get_hospital(self, obj):
		try:
			return  obj.proctors_pivot_id.get(status = True).hospital.hospital_name
		except:
			return None

	def get_area_of_experties(self, obj):
		try:
			return obj.area_of_experties.id
		except:
			return ''

	def get_spoken_languages(self, obj):
		try:
			return obj.spoken_languages.id
		except:
			return ''

	def get_approach(self, obj):
		try:
			return obj.approach.id
		except:
			return ''

	def get_products(self, obj):
		try:
			return obj.products.id
		except:
			return ''



class ProctorsZoneViewSerializer(serializers.ModelSerializer):
	proctor_name = serializers.SerializerMethodField(read_only = True)
	proctor_image = serializers.SerializerMethodField(read_only= True)
	proctor_id = serializers.SerializerMethodField(read_only= True)
	country = serializers.SerializerMethodField(read_only=True)
	hospital = serializers.SerializerMethodField(read_only=True)
	class Meta:
		model = Proctors
		fields = ['proctor_name', 'proctor_image', 'proctor_id', 'country', 'hospital']

	def get_proctor_name(self, obj):
		try:
			return obj.user.name
		except:
			return None

	def get_proctor_id(self, obj):
		try:
			return obj.id
		except:
			return None

	def get_proctor_image(self, obj):
		try:
			return obj.user.image.url
		except:
			return None

	def get_hospital(self, obj):
		try:
			return  obj.proctors_pivot_id.get(status = True).hospital.hospital_name
		except:
			return None

	def get_country(self, obj):
		try:
			return obj.user.country.name
		except:
			return None



class ProctorsZoneDropViewSerializer(serializers.ModelSerializer):
	proctor_name = serializers.SerializerMethodField(read_only = True)
	proctor_id = serializers.SerializerMethodField(read_only= True)
	class Meta:
		model = Proctors
		fields = ['proctor_name', 'proctor_id']

	def get_proctor_name(self, obj):
		try:
			return obj.user.name
		except:
			return None

	def get_proctor_id(self, obj):
		try:
			return obj.id
		except:
			return None


class ProctorsNotAvailalbeViewSerializer(serializers.ModelSerializer):
	proctor_name = serializers.SerializerMethodField(read_only = True)
	class Meta:
		model = Proctors
		fields = ['proctor_name']

	def get_proctor_name(self, obj):
		try:
			return obj.user.name
		except:
			return None