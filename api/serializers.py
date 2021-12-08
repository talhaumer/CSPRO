from django.db import transaction
from rest_framework import serializers
from api.models import Products,HospitalCountires, Hospital, Hcp_role, Languages, Solution, Audience, Region, Approach, AreaOfExperties, \
	EventType, Speciality
from api.zone.serializers  import ZoneSerializer, CountriesSerializer
from django.contrib.auth import get_user_model
from api.zone.models import Countries, Zone
import json 


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


class ProductsSerializer(serializers.ModelSerializer):
	product_name = serializers.CharField(required= True)
	# product_typology = serializers.CharField(required= True)
	# product_type = serializers.CharField(required= True)
	image = serializers.ImageField(max_length=None, use_url=True)
	image_up = serializers.CharField(required=False)
	class Meta:
		model = Products
		fields = ('id', 'product_name','image', "image_up")
		# read_only_fields = ('created','updated')
	def create(self, validated_data):
		return Products.objects.create(**validated_data)

	def update(self, instance, validated_data):
		instance.product_name = validated_data.get('product_name', instance.product_name)
		instance.image = validated_data.get('image_up', instance.image)
		# instance.product_typology = validated_data.get('product_typology', instance.product_typology)
		# instance.product_type = validated_data.get('product_type', instance.product_type)
		instance.save()
		return instance


class ProductsViewSerializer(serializers.ModelSerializer):
	product_name = serializers.CharField(read_only = True)
	image = serializers.ImageField(max_length=None, use_url=True)
	class Meta:
		model = Products
		fields = ['id', 'image', 'product_name']


class HospitalSerializer(serializers.ModelSerializer):
	hospital_name = serializers.CharField(required =  True)
	number_of_trainee = serializers.IntegerField(required = True)
	products = serializers.StringRelatedField(many = True, read_only = True)
	country = serializers.SerializerMethodField(read_only=True)
	location = serializers.CharField(required = True)
	is_it_preceptorship = serializers.BooleanField(required= True)
	qualified_for_news_mics_program = serializers.BooleanField(required = True)
	cognos_id  = serializers.CharField(required = True)
	country_id = serializers.IntegerField(write_only = True)
	products_id = serializers.ListField(write_only = True)
	class Meta:
		model = Hospital
		fields = ('id', 'hospital_name', 'number_of_trainee','products_id', 'products', 'country', 'country_id', 'location', 'is_it_preceptorship', 'qualified_for_news_mics_program', 'cognos_id')


	def create(self, validated_data):
		try:
			with transaction.atomic():
				x = validated_data.pop('products_id')
				country_id = validated_data.pop('country_id')
				hospital = Hospital.objects.create(**validated_data)
				hospital_countries = HospitalCountires.objects.create(
					country = Countries.objects.get(id = country_id),
					hospital = hospital
				)
				for product in x:
					product_obj = Products.objects.get(id= product)
					hospital.products.add(product_obj)

				hospital.save()
				return hospital
		except Exception as e:
			return e

	def get_country(self, obj):
		try:
			return obj.hospital_id.get().country.name
		except:
			return ''

	def get_products(self, obj):
		try:
			return obj.products.product_name
		except:
			return ''



class HospitalUpdateSerializer(serializers.ModelSerializer):
	hospital_name = serializers.CharField(required =  False)
	number_of_trainee = serializers.IntegerField(required = False)
	products = serializers.PrimaryKeyRelatedField(many = True, read_only = True)
	country = serializers.SerializerMethodField(read_only=False)
	location = serializers.CharField(required = False)
	is_it_preceptorship = serializers.BooleanField(required= False)
	qualified_for_news_mics_program = serializers.BooleanField(required = False)
	cognos_id  = serializers.CharField(required = False)
	country_id = serializers.IntegerField(write_only=True, allow_null=True)
	products_id = serializers.ListField(required = False)
	# replace = serializers.ListField(write_only = True)
	class Meta:
		model = Hospital
		fields = ('id', 'hospital_name', 'number_of_trainee','products_id', 'products', 'country', 'country_id', 'location', 'is_it_preceptorship', 'qualified_for_news_mics_program', 'cognos_id')


	def update(self, instance, validated_data):
		x = validated_data.pop('products_id')
		# print(x)

		instance.hospital_name = validated_data.get('hospital_name', instance.hospital_name)
		instance.number_of_trainee = validated_data.get('number_of_trainee', instance.number_of_trainee)
		if "country_id" in validated_data.keys():
			country_id = validated_data.pop('country_id')
			data = {}
			data['country'] = Countries.objects.get(id= country_id)
			countries_instance = HospitalCountires.objects.get(hospital__id=instance.id)
			countries_instance.country = data.get('country', countries_instance.country)
			countries_instance.save()

		instance.location = validated_data.get('location', instance.location)
		instance.is_it_preceptorship = validated_data.get('is_it_preceptorship', instance.is_it_preceptorship)
		instance.qualified_for_news_mics_program = validated_data.get('qualified_for_news_mics_program', instance.qualified_for_news_mics_program)
		instance.cognos_id = validated_data.get('cognos_id', instance.cognos_id)
		if x:
			instance.products.clear()
			instance.products.add(*x)
		instance.save()
		return instance

	def get_country(self, obj):
		try:
			return obj.hospital_id.get().country.id
		except:
			return None

	def get_products(self, obj):
		try:
			return obj.products.id
		except:
			return ''


class HospitalNameSerializer(serializers.ModelSerializer):
	hospital_name = serializers.CharField(read_only=True)
	number_of_trainee = serializers.IntegerField(read_only=True)

	class Meta:
		model = Hospital
		fields = ["id", "hospital_name", "number_of_trainee"]

class ProductsNameSerializer(serializers.ModelSerializer):
	product_name = serializers.CharField()
	class Meta:
		model = Products
		fields = ["id","product_name"]
		# read_only_fields = ('created','updated')

class ZoneViewSerializer(serializers.ModelSerializer):
	zone = serializers.CharField()
	class Meta:
		model = Zone
		fields = ["id", "zone"]




""" Proctors Payload 
{
  "gender": "Male",
  "relationship": "Single",
  "products": [
    {
      "product_name": "Perceval"
    },
    {
      "product_name": "Solo Smart"
    }
  ],
  "hospital": {
    "hospital_name": "Mayo Hospital"
  },
  "name": "Talha Umer",
  "email": "talha12@gmail.com",
  "address": "plaza no 56 Appartment no 401 surahi chowk bahria town",
  "telephone": "+923026013335",
  "fax ": "somethingisfaxthatIdon 't know",
  "publication": "A number of papers in my  field of research",
  "nationality": "Pakistani",
  "data_of_birth": "1999-11-02",
  "place_of_birth": {
    "name": "Pakistan"
  }
}
"""



class HcpRoleSerializer(serializers.ModelSerializer):
	name_of_role = serializers.CharField(read_only= True)
	code = serializers.CharField(read_only=True)
	
	class Meta:
		model = Hcp_role
		fields = ('id', 'name_of_role', 'code')
		read_only_fields = ('created','updated')
	# def create(self, validated_data):
	# 	# print(validated_data.name)
	# 	return Hcp_role.objects.create(**validated_data)
	#
	# def update(self, instance, validated_data):
	# 	instance.name = validated_data.get('name', instance.name)
	# 	instance.save()
	# 	return instance


class LanguagesSerializer(serializers.ModelSerializer):
	language = serializers.CharField(required= True)
	
	class Meta:
		model = Languages
		fields = ('id', 'language',)
		read_only_fields = ('created','updated')

	def create(self, validated_data):
		# print(validated_data.name)
		return Languages.objects.create(**validated_data)

	def update(self, instance, validated_data):
		instance.language = validated_data.get('language', instance.language)
		instance.save()
		return instance


class SolutionSerializer(serializers.ModelSerializer):
	solution = serializers.CharField(required= True)
	
	class Meta:
		model = Solution
		fields = ('id', 'solution',)
		read_only_fields = ('created','updated')

	def create(self, validated_data):
		# print(validated_data.name)
		return Solution.objects.create(**validated_data)

	def update(self, instance, validated_data):
		instance.solution = validated_data.get('solution', instance.solution)
		instance.save()
		return instance

class AudienceSerializer(serializers.ModelSerializer):
	audience = serializers.CharField(required= True)
	
	class Meta:
		model = Audience
		fields = ('id', 'audience',)
		read_only_fields = ('created','updated')

	def create(self, validated_data):
		# print(validated_data.name)
		return Audience.objects.create(**validated_data)

	def update(self, instance, validated_data):
		instance.audience = validated_data.get('audience', instance.audience)
		instance.save()
		return instance


class RegionSerializer(serializers.ModelSerializer):
	region = serializers.CharField(required= True)
	
	class Meta:
		model = Region
		fields = ('id', 'region',)
		read_only_fields = ('created','updated')

	def create(self, validated_data):
		# print(validated_data.name)
		return Region.objects.create(**validated_data)

	def update(self, instance, validated_data):
		instance.region = validated_data.get('region', instance.region)
		instance.save()
		return instance




class ApproachSerializer(serializers.ModelSerializer):
	name = serializers.CharField(read_only = True)
	
	class Meta:
		model = Approach
		fields = ('id', 'name',)


class AreaOfExpertiesSerializer(serializers.ModelSerializer):
	name = serializers.CharField(read_only = True)
	
	class Meta:
		model = AreaOfExperties
		fields = ('id', 'name',)


class HospitalViewSerializer(serializers.ModelSerializer):
	hospital_name = serializers.CharField(required =  True)
	number_of_trainee = serializers.IntegerField(required = True)
	products = serializers.StringRelatedField(many = True, read_only = True)
	country = serializers.SerializerMethodField(read_only=True)
	location = serializers.CharField(required = True)
	qualified_for_news_mics_program = serializers.BooleanField(required = True)
	cognos_id  = serializers.CharField(required = True)
	class Meta:
		model = Hospital
		fields = ('id', 'hospital_name', 'number_of_trainee', 'products', 'country', 'location', 'qualified_for_news_mics_program', 'cognos_id')


	def get_country(self, obj):
		try:
			res = []
			for each in obj.hospital_id.all():
				res.append(each.country.name)
			return res
		except:
			return None

	# def get_products(self, obj):
	# 	try:
	# 		return obj.products.id
	# 	except:
	# 		return ''


class EventSerializer(serializers.ModelSerializer):
	name = serializers.CharField(read_only=True)
	code = serializers.CharField(read_only=True)

	class Meta:
		model = EventType
		fields = ["id", "name", "code"]



class SpecialitySerializer(serializers.ModelSerializer):
	name = serializers.CharField(read_only=True)
	code = serializers.CharField(read_only=True)

	class Meta:
		model = Speciality
		fields = ["id", "name", "code"]