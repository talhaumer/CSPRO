from rest_framework import serializers

from api.proctorship.models import ConstantData
from api.trainee.models  import TraineeProfile
from api.models import Hospital
from api.zone.models import Countries


class TrainProctorshipSerializer(serializers.ModelSerializer):
	title = serializers.CharField(read_only = True)
	name = serializers.CharField(read_only = True)
	surname = serializers.CharField(read_only = True)
	corcym_accompanying_rep = serializers.CharField(read_only = True)
	current_preferential = serializers.CharField(read_only = True)
	mvr_case_per_year = serializers.IntegerField(read_only = True)
	mvr_case_per_year_by_trainee = serializers.IntegerField(read_only =True)
	note = serializers.CharField(read_only = True, allow_null=True, allow_blank=True)
	hospital = serializers.SerializerMethodField(read_only = True)
	country = serializers.SerializerMethodField(read_only = True)
	status = serializers.BooleanField(read_only=True)
	revoke = serializers.BooleanField(read_only=True)
	interest_invasive = serializers.BooleanField(read_only=True)


	class Meta:
		model = TraineeProfile
		fields = ['id', 'hospital', 'country','title', 'status','revoke','name', 'surname', 'corcym_accompanying_rep', 'current_preferential', 'mvr_case_per_year', 'mvr_case_per_year_by_trainee', 'note', 'interest_invasive']

	def get_hospital(self, obj):
		try:
			return obj.hospital.hospital_name
		except:
			return ""

	def get_country(self, obj):
		try:
			return obj.country.name
		except:
			return ""


class TrainSerializer(serializers.ModelSerializer):
	proctorship = serializers.SerializerMethodField(read_only = True)
	title = serializers.CharField(required = True)
	name = serializers.CharField(required = True)
	surname = serializers.CharField(required = True)
	corcym_accompanying_rep = serializers.CharField(required = True)
	current_preferential = serializers.CharField(required = True)
	mvr_case_per_year = serializers.IntegerField(required = True)
	mvr_case_per_year_by_trainee = serializers.IntegerField(required =True)
	note = serializers.CharField(required = True, allow_blank=True, allow_null=True)
	hospital = serializers.SerializerMethodField(read_only = True)
	hospital_id = serializers.IntegerField(write_only = True)
	country = serializers.SerializerMethodField(read_only = True)
	country_id = serializers.IntegerField(write_only = True)
	proctorship_id = serializers.IntegerField(required = False)
	status = serializers.BooleanField(read_only = True)
	interest_invasive = serializers.BooleanField(required=True)


	class Meta:
		model = TraineeProfile
		fields = ['id','proctorship','status','interest_invasive','proctorship_id', 'hospital', 'hospital_id', 'country', 'country_id','title', 'name', 'surname', 'corcym_accompanying_rep', 'current_preferential', 'mvr_case_per_year', 'mvr_case_per_year_by_trainee', 'note']

	def  create(self, validated_data):
		title = validated_data.pop('title')
		current_preferential = validated_data.pop('current_preferential')
		trainee = TraineeProfile.objects.create(**validated_data)
		trainee.title = ConstantData.objects.get(code = title)
		trainee.current_preferential = ConstantData.objects.get(code=current_preferential)
		trainee.save()
		return trainee

	def get_hospital(self, obj):
		try:
			return obj.hospital.name
		except:
			return ""

	def get_country(self, obj):
		try:
			return obj.country.name
		except:
			return ""

	def get_proctorship(self, obj):
		try:
			return obj.proctorship.id
		except:
			return ""

	def get_preceptorship(self, obj):
		try:
			return obj.preceptorship.id
		except:
			return ""

	def get_master_proctorship(self, obj):
		try:
			return obj.master_proctorship.id
		except:
			return ""


class TraineeUpdateSerializer(serializers.ModelSerializer):
	# proctorship = serializers.SerializerMethodField(read_only = True)
	# preceptorship = serializers.SerializerMethodField(read_only = True)
	# master_proctorship = serializers.SerializerMethodField(read_only = True)
	title = serializers.CharField(required = False)
	name = serializers.CharField(required = False)
	surname = serializers.CharField(required = False)
	corcym_accompanying_rep = serializers.CharField(required = False)
	current_preferential = serializers.CharField(required = False)
	mvr_case_per_year = serializers.IntegerField(required = False)
	mvr_case_per_year_by_trainee = serializers.IntegerField(required =False)
	note = serializers.CharField(required = False, allow_null=True, allow_blank=True)
	hospital = serializers.SerializerMethodField(read_only = False)
	# hospital_id = serializers.IntegerField(write_only = True)
	country = serializers.SerializerMethodField(read_only = False)
	# country_id = serializers.IntegerField(write_only = True)
	interest_invasive = serializers.BooleanField(write_only=False)

	class Meta:
		model = TraineeProfile
		fields = ['id','hospital','interest_invasive', 'country','title', 'name', 'surname', 'corcym_accompanying_rep', 'current_preferential', 'mvr_case_per_year', 'mvr_case_per_year_by_trainee', 'note']
		# fields = ['proctorship','master_proctorship', 'preceptorship', 'hospital', 'hospital_id', 'country', 'country_id','title', 'name', 'surname', 'corcym_accompanying_rep', 'current_preferential', 'mvr_case_per_year', 'mvr_case_per_year_by_trainee', 'note']

	def update(self, instance, validated_data):
		try:
			instance.name = validated_data.get('name', instance.name)
			instance.surname = validated_data.get('surname', instance.surname)
			if 'title' in validated_data.keys():
				title = validated_data.pop('title')
				validated_data['title'] = ConstantData.objects.get(code=title)
				instance.title = validated_data.get('title', instance.title)

			instance.corcym_accompanying_rep = validated_data.get('corcym_accompanying_rep',
																  instance.corcym_accompanying_rep)
			if 'current_preferential' in validated_data.keys():
				current_preferential = validated_data.pop('current_preferential')
				validated_data['current_preferential'] = ConstantData.objects.get(code=current_preferential)
				instance.current_preferential = validated_data.get('current_preferential', instance.current_preferential)
			instance.mvr_case_per_year = validated_data.get('mvr_case_per_year', instance.mvr_case_per_year)
			instance.mvr_case_per_year_by_trainee = validated_data.get('mvr_case_per_year_by_trainee',
																	   instance.mvr_case_per_year_by_trainee)
			# validated_data['hospital'] = Hospital.objects.get(pk=validated_data.pop('hospital_id'))
			# instance.hospital = validated_data.get('hospital', instance.hospital)
			# validated_data['country'] = Countries.objects.get(pk=validated_data.pop('country_id'))
			# instance.country = validated_data.get('country', instance.country)
			instance.note = validated_data.get('note', instance.note)
			instance.interest_invasive = validated_data.get('interest_invasive', instance.interest_invasive)
			instance.save()
			return instance
		except Exception as e:
			return e

	def get_hospital(self, obj):
		try:
			return obj.hospital.id
		except:
			return ""

	def get_country(self, obj):
		try:
			return obj.country.id
		except:
			return ""

	def get_proctorship(self, obj):
		try:
			return obj.proctorship.id
		except:
			return ""

	def get_preceptorship(self, obj):
		try:
			return obj.preceptorship.id
		except:
			return ""

	def get_master_proctorship(self, obj):
		try:
			return obj.master_proctorship.id
		except:
			return ""
