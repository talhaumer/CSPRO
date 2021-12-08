from collections import OrderedDict

from django.db import transaction
from django.db.models import Count
from rest_framework import serializers

from api.feedback.models import Rating
from api.models import Hospital
from api.preceptorship.models import Preceptorship, PreceptorshipProctors, TraineePreceptorshipProfile, \
	PreceptorshipStatus, PreceptorshipProposal, PreceptorshipTraineeUploads, InvoicePerceptorship, \
	AttendanceFormPerceptorship
from api.proctors.models import Proctors
from api.proctorship.models import ConstantData
from api.status.models import StatusConstantData
from api.users.models import User
from api.zone.models import ZoneCountries, Countries
from cspro.utils import activity_id


class PreceptorshipSerializer(serializers.ModelSerializer):
	user = serializers.SerializerMethodField(read_only=True)
	is_global = serializers.BooleanField(required=True)
	product = serializers.SerializerMethodField(read_only=True)
	secondary_product = serializers.SerializerMethodField(read_only=True)
	start_date = serializers.DateField(write_only=True)
	end_date = serializers.DateField(write_only=True)
	hospital = serializers.SerializerMethodField(read_only=True)
	note = serializers.CharField(required=True, allow_null=True, allow_blank=True)
	training_type = serializers.CharField(required=True, allow_null=True, allow_blank=True)
	types_of_first_training = serializers.CharField(required=True, allow_null=True, allow_blank=True)
	type_advance_training = serializers.CharField(required=True, allow_null=True, allow_blank=True)
	specific_training = serializers.CharField(required=True, allow_null=True, allow_blank=True)
	not_implant_regularly = serializers.CharField(required=True, allow_null=True, allow_blank=True)
	hospital_id = serializers.IntegerField(write_only=True)
	product_id = serializers.IntegerField(write_only=True)
	secondary_product_id = serializers.IntegerField(write_only=True, allow_null=True)
	proctor_id = serializers.IntegerField(write_only=True)
	user_id = serializers.IntegerField(write_only=True)
	# zone_countries_id = serializers.IntegerField(write_only=True)
	zone_id = serializers.IntegerField(write_only=True)
	trainee_profile = serializers.ListField(write_only=True)

	class Meta:
		model = Preceptorship
		fields = ["user", "is_global", "product", "product_id", "secondary_product_id", "secondary_product",
				  "start_date", "end_date", "hospital", "note", "training_type", "types_of_first_training",
				  "type_advance_training", "specific_training",
				  "not_implant_regularly", "proctor_id", "hospital_id", "user_id", 'trainee_profile', "zone_id"]

	def create(self, validated_data):
		try:
			with transaction.atomic():
				training_type = validated_data.pop('training_type')
				user_id = validated_data.pop('user_id')
				types_of_first_training = validated_data.pop('types_of_first_training')
				type_advance_training = validated_data.pop('type_advance_training')
				specific_training = validated_data.pop('specific_training')
				not_implant_regularly = validated_data.pop('not_implant_regularly')
				# zone_countries_id = validated_data.pop('zone_countries_id')
				# zone_id = validated_data.pop('zone_id')
				trainee = validated_data.pop('trainee_profile')
				proctor_id = validated_data.pop('proctor_id')
				start_date = validated_data.pop('start_date')
				end_date = validated_data.pop('end_date')
				validated_data['user_id'] = user_id

				preceptorship = Preceptorship.objects.create(**validated_data)
				num = preceptorship.id
				char = "PRG"
				if not preceptorship.is_global:
					char = "PRL"
				preceptorship.activity_id = activity_id(char, num)

				if training_type:
					preceptorship.training_type = ConstantData.objects.get(code=training_type)

				if types_of_first_training:
					preceptorship.types_of_first_training = ConstantData.objects.get(code=types_of_first_training)

				if type_advance_training:
					preceptorship.type_advance_training = ConstantData.objects.get(code=type_advance_training)

				if specific_training:
					preceptorship.specific_training = ConstantData.objects.get(code=specific_training)

				if not_implant_regularly:
					preceptorship.not_implant_regularly = ConstantData.objects.get(code=not_implant_regularly)

				# if zone_countries_id and zone_id:
				# 	preceptorship.zone_countries = ZoneCountries.objects.get(zone__id=zone_id,
				# 															 countries__id=zone_countries_id)

				for trainee_profile in trainee:
					TraineePreceptorshipProfile.objects.create(
						preceptorship=preceptorship,
						name=trainee_profile['name'],
						surname=trainee_profile['surname'],
						title=ConstantData.objects.get(code=trainee_profile['title']),
						mvr_case_per_year=trainee_profile['mvr_case_per_year'],
						current_preferential=ConstantData.objects.get(code=trainee_profile['current_preferential']),
						mvr_case_per_year_by_trainee=trainee_profile['mvr_case_per_year_by_trainee'],
						note=trainee_profile['note'],
						corcym_accompanying_rep=trainee_profile['corcym_accompanying_rep'],
						country=Countries.objects.get(id=trainee_profile['country_id']),
						hospital=Hospital.objects.get(id=trainee_profile['hospital_id']),
						interest_invasive=trainee_profile['interest_invasive']
					)

				status_data = {'status': StatusConstantData.objects.get(code='pending'),
							   'preceptorship_activity': preceptorship, 'user': User.objects.get(id=user_id)}
				status_data = PreceptorshipStatus.objects.create(**status_data)
				porposal = PreceptorshipProposal.objects.create(
					**{'status': status_data, 'start_date': start_date, 'end_date': end_date})

				if proctor_id:
					proctors = {
						'preceptorship_proposal': porposal,
						'proctors': Proctors.objects.get(id=proctor_id),
					}
					a = PreceptorshipProctors.objects.create(**proctors)

				preceptorship.save()
				return preceptorship
		except Exception as e:
			return e

	def get_user(self, obj):
		try:
			return obj.user.name
		except:
			return None

	def get_country(self, obj):
		try:
			return obj.country.name
		except:
			return None

	def get_hospital(self, obj):
		try:
			return obj.hospital.hospital_name
		except:
			return None

	def get_secondary_product(self, obj):
		try:
			return obj.secondary_product.product_name
		except:
			return None

	def get_product(self, obj):
		try:
			return obj.product.product_name
		except:
			return None




class PreceptorshipProctorsSerializer(serializers.ModelSerializer):
	proctors = serializers.SerializerMethodField(read_only = True)
	status = serializers.BooleanField(read_only=True)
	proctor_order = serializers.IntegerField(read_only=True)
	class Meta:
		model = PreceptorshipProctors
		fields = ['proctors', 'status', 'proctor_order']

	def get_proctors(self, obj):
		try:
			return obj.proctors.user.name
		except:
			return None

class PreceptorshipProposalSerializer(serializers.ModelSerializer):
	proctor_user_id = serializers.IntegerField(write_only=True)
	start_date = serializers.DateField(required=True)
	end_date = serializers.DateField(required=True)
	note = serializers.CharField(required=True, allow_null=True, allow_blank=True)
	proctors = serializers.SerializerMethodField(read_only=True)

	class Meta:
		model = PreceptorshipProposal
		fields = ['id','proctor_user_id', 'note', 'end_date', 'start_date', 'proctors']

	def get_proctor_user(self, obj):
		try:
			return obj.get_proctor_user.name
		except:
			return None

	def get_user(self, obj):
		try:
			return obj.user.name
		except:
			return None

	def get_proctors(self, obj):
		try:
			return PreceptorshipProctorsSerializer(obj.proctor_porposal.proctors, many=True).data
		except:
			return None


class PreceptorshipProposalViewSerializer(serializers.ModelSerializer):
	# user = serializers.SerializerMethodField(read_only = True)
	proctor = serializers.SerializerMethodField(read_only=True)
	start_date = serializers.DateField(required=True)
	end_date = serializers.DateField(required=True)
	note = serializers.CharField(required=True, allow_null=True, allow_blank=True)

	class Meta:
		model = PreceptorshipProposal
		fields = ['id','proctor', 'note', 'end_date', 'start_date']

	def get_proctor(self, obj):
		try:
			return PreceptorshipProctorsSerializer(obj.preceptorship_porposal.all(), many=True).data
		except:
			return None


class PreceptorshipStatusSerializer(serializers.ModelSerializer):
	user = serializers.SerializerMethodField(read_only = True)
	status = serializers.CharField(required = True)
	user_id = serializers.IntegerField(write_only=True)
	perceptorship_activity_id = serializers.IntegerField(write_only=True)
	date = serializers.DateField(read_only=True)
	purposal = serializers.SerializerMethodField(read_only=True)
	alternatives_data = PreceptorshipProposalSerializer(required=False)
	code = serializers.CharField(read_only=True)
	reason = serializers.CharField(required=False)

	class Meta:
		model = PreceptorshipStatus
		fields = ['id','user','status', 'user_id', 'reason','perceptorship_activity_id','code', 'date', 'purposal', 'alternatives_data']

	def create(self, validated_data):
		try:
			with transaction.atomic():
				alternatives_data = OrderedDict()
				if 'alternatives_data' in validated_data.keys():
					alternatives_data = validated_data.pop('alternatives_data')

				perceptorship_activity_id = validated_data.pop('perceptorship_activity_id')
				validated_data['preceptorship_activity_id'] = perceptorship_activity_id

				PreceptorshipStatus.objects.filter(preceptorship_activity__id=perceptorship_activity_id).update(is_active=False)
				status = validated_data.pop('status')
				user_id = validated_data.pop('user_id')
				validated_data['user_id'] = user_id
				validated_data ['status'] = StatusConstantData.objects.get(code = status)
				status = PreceptorshipStatus.objects.create(**validated_data)

				if len(alternatives_data) != 0:
					data_add = {
						'status':status,
						'note':alternatives_data['note'],
						'start_date':alternatives_data['start_date'],
						'end_date':alternatives_data['end_date']
					}
					alt = PreceptorshipProposal.objects.create(**data_add)
					if 'proctor_user_id' in alternatives_data.keys():
						qs = PreceptorshipProctors.objects.filter(preceptorship_proposal__status__preceptorship_activity__id=perceptorship_activity_id, status = True)
						if qs:
							qs.update(status = False)
						proctors = {
							'preceptorship_proposal': alt,
							'proctors': Proctors.objects.get(id=alternatives_data['proctor_user_id']),
							}
						alpha = PreceptorshipProctors.objects.create(**proctors)

				status.save()
				return status
		except Exception as e:
			return e

	def get_user(self, obj):
		try:
			return obj.user.name
		except:
			return None

	def get_purposal(self, obj):
		try:
			return PreceptorshipProposalViewSerializer(obj.alter_proctorship_porposal.get()).data
		except:
			return None


class PreceptorshipStatusViewSerializer(serializers.ModelSerializer):
	user = serializers.SerializerMethodField(read_only = True)
	status = serializers.SerializerMethodField(read_only=True)
	code = serializers.SerializerMethodField(read_only=True)
	date = serializers.DateField(read_only=True)
	reason  = serializers.CharField(read_only=True)
	alternatives = serializers.SerializerMethodField(read_only=True)
	class Meta:
		model = PreceptorshipStatus
		fields = ['id','user','status','code', 'date', 'alternatives','reason']

	def get_user(self, obj):
		try:
			return obj.user.name
		except:
			return None

	def get_alternatives(self, obj):
		try:
			return PreceptorshipProposalViewSerializer(obj.alter_preceptorship_porposal.get()).data
		except:
			return None

	def get_status(self, obj):
		try:
			return  obj.status.name
		except:
			return None

	def get_code(self, obj):
		try:
			return  obj.status.code
		except:
			return None


class PreceptorshipViewSerializer(serializers.ModelSerializer):
	user = serializers.SerializerMethodField(read_only=True)
	is_global = serializers.BooleanField(read_only=True)
	product = serializers.SerializerMethodField(read_only=True)
	product_id = serializers.SerializerMethodField(read_only=True)
	secondary_product = serializers.SerializerMethodField(read_only=True)
	secondary_product_id = serializers.SerializerMethodField(read_only=True)
	hospital = serializers.SerializerMethodField(read_only=True)
	hospital_id = serializers.SerializerMethodField(read_only=True)
	note = serializers.CharField(read_only=True)
	training_type = serializers.CharField(read_only=True)
	types_of_first_training = serializers.CharField(read_only = True)
	type_advance_training = serializers.CharField(read_only=True)
	specific_training = serializers.CharField(read_only=True)
	not_implant_regularly = serializers.CharField(read_only=True)
	status = serializers.SerializerMethodField(read_only=True)
	rem_seats = serializers.SerializerMethodField(read_only=True)
	activity_id = serializers.CharField(read_only=True)

	class Meta:
		model = Preceptorship
		fields = ['id',"user", "is_global", "product","product_id","secondary_product","secondary_product_id", "hospital", "hospital_id","note", "training_type", "types_of_first_training",
				  "type_advance_training", "specific_training","status","not_implant_regularly", "rem_seats", "activity_id"]
		# fields = "__all__"
	def get_user(self, obj):
		try:
			return obj.user.name
		except:
			return None

	def get_country(self, obj):
		try:
			return obj.country.name
		except:
			return None

	def get_hospital(self, obj):
		try:
			return obj.hospital.hospital_name
		except:
			return None

	def get_hospital_id(self, obj):
		try:
			return obj.hospital.id
		except:
			return None


	def get_secondary_product(self, obj):
		try:
			return obj.secondary_product.product_name
		except:
			return None

	def get_secondary_product_id(self, obj):
		try:
			return obj.secondary_product.id
		except:
			return None

	def get_product(self, obj):
		try:
			return obj.product.product_name
		except:
			return None

	def get_product_id(self, obj):
		try:
			return obj.product.id
		except:
			return None

	def get_status(self, obj):
		try:
			return PreceptorshipStatusViewSerializer(obj.preceptorshipStatus_status.all(), many=True).data
		except:
			return None

	def get_rem_seats(self, obj):
		try:
			hospital = obj.hospital.number_of_trainee
			traine = TraineePreceptorshipProfile.objects.filter(preceptorship__id=obj.id, revoke=False)
			rem = hospital - traine.count()
			if rem > 0:
				return rem
			else:
				return 0
		except:
			return None

class TraineePreceptorshipSerializer(serializers.ModelSerializer):
	preceptorship_id = serializers.IntegerField(write_only=True)
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
	status = serializers.BooleanField(read_only = True)
	interest_invasive = serializers.BooleanField(required=True)
	revoke = serializers.BooleanField(read_only=True)


	class Meta:
		model = TraineePreceptorshipProfile
		fields = ['id','status','revoke','preceptorship_id','interest_invasive', 'hospital', 'hospital_id', 'country', 'country_id','title', 'name', 'surname', 'corcym_accompanying_rep', 'current_preferential', 'mvr_case_per_year', 'mvr_case_per_year_by_trainee', 'note']

	def create(self, validated_data):
		try:
			with transaction.atomic():
				title = validated_data.pop('title')
				current_preferential = validated_data.pop('current_preferential')
				trainee = TraineePreceptorshipProfile.objects.create(**validated_data)
				trainee.title = ConstantData.objects.get(code=title)
				trainee.current_preferential = ConstantData.objects.get(code=current_preferential)
				trainee.save()
				return trainee
		except Exception as e:
			return e

	def get_hospital(self, obj):
		try:
			return obj.hospital.hospital_name
		except:
			return None

	def get_country(self, obj):
		try:
			return obj.country.name
		except:
			return None

class TraineeUpdatePreceptorshipSerializer(serializers.ModelSerializer):
	# preceptorship_id = serializers.IntegerField(write_only=True)
	title = serializers.CharField(required=False)
	name = serializers.CharField(required=False)
	surname = serializers.CharField(required=False)
	corcym_accompanying_rep = serializers.CharField(required=False)
	current_preferential = serializers.CharField(required=False)
	mvr_case_per_year = serializers.IntegerField(required=False)
	mvr_case_per_year_by_trainee = serializers.IntegerField(required=False)
	note = serializers.CharField(required=False, allow_null=True, allow_blank=True)
	hospital = serializers.SerializerMethodField(read_only=False)
	hospital_id = serializers.IntegerField(write_only=False)
	country = serializers.SerializerMethodField(read_only=False)
	country_id = serializers.IntegerField(write_only=False)
	status = serializers.BooleanField(read_only=True)
	interest_invasive = serializers.BooleanField(required=False)

	class Meta:
		model = TraineePreceptorshipProfile
		fields = ['id', 'status', 'interest_invasive', 'hospital', 'hospital_id', 'country',
				  'country_id', 'title', 'name', 'surname', 'corcym_accompanying_rep', 'current_preferential',
				  'mvr_case_per_year', 'mvr_case_per_year_by_trainee', 'note']

	def update(self, instance,validated_data):
		instance.name = validated_data.get('name', instance.name)
		instance.surname = validated_data.get('surname', instance.surname)
		if 'title' in validated_data.keys():
			title = validated_data.pop('title')
			validated_data['title'] = ConstantData.objects.get(code = title)
			instance.title = validated_data.get('title', instance.title)

		instance.corcym_accompanying_rep = validated_data.get('corcym_accompanying_rep',
															  instance.corcym_accompanying_rep)
		if 'current_preferential' in validated_data.keys():
			current_preferential = validated_data.pop('current_preferential')
			validated_data['current_preferential'] = ConstantData.objects.get(code = current_preferential)
			instance.current_preferential = validated_data.get('current_preferential', instance.current_preferential)
		instance.mvr_case_per_year = validated_data.get('mvr_case_per_year', instance.mvr_case_per_year)
		instance.mvr_case_per_year_by_trainee = validated_data.get('mvr_case_per_year_by_trainee',
																   instance.mvr_case_per_year_by_trainee)
		instance.note = validated_data.get('note', instance.note)
		instance.interest_invasive = validated_data.get('interest_invasive', instance.interest_invasive)
		if 'hospital_id' in validated_data.keys():
			validated_data['hospital'] = Hospital.objects.get(id = validated_data.pop('hospital_id'))
			instance.hospital = validated_data.get('hospital', instance.hospital)

		if 'country_id' in validated_data.keys():
			validated_data['country'] = Countries.objects.get(id = validated_data.pop('country_id'))
			instance.country = validated_data.get('country', instance.country)

		instance.save()
		return instance


	def get_hospital(self, obj):
		try:
			return obj.hospital.hospital_name
		except:
			return None

	def get_country(self, obj):
		try:
			return obj.country.name
		except:
			return None


class PreceptorshipTraineeUploadsSerializers(serializers.ModelSerializer):
	preceptorship_trainee_id = serializers.IntegerField(required = True)
	rate_of_demostration = serializers.CharField(required=True)
	rate_experince_in_operating_room = serializers.CharField(required=True)
	rate_hospital_facility = serializers.CharField(required=True)
	number_of_patients = serializers.IntegerField(required=True)
	number_of_perceval = serializers.IntegerField(required=True)
	rate_of_experince_overall = serializers.CharField(required=True)
	percevel_driver = serializers.CharField(required=False, allow_blank=True, allow_null=True)
	rate_level_of_training = serializers.CharField(required=True)
	are_intrested_learning_more = serializers.BooleanField(required=True)
	rate_corcym_support = serializers.CharField(required=True)
	corcym_suggestion = serializers.CharField(required=True)
	proctor_report = serializers.FileField(required=True)
	is_memo_family = serializers.BooleanField(required=True)
	is_perceval = serializers.BooleanField(required=True)
	is_solo_smart = serializers.BooleanField(required=True)
	class Meta:
		model = PreceptorshipTraineeUploads
		fields = ['id','preceptorship_trainee_id','percevel_driver','is_memo_family','is_perceval','is_solo_smart','rate_of_demostration','rate_experince_in_operating_room','rate_hospital_facility','number_of_patients', 'number_of_perceval', 'rate_of_experince_overall', 'rate_level_of_training', 'are_intrested_learning_more','rate_corcym_support', 'proctor_report', 'corcym_suggestion']

	def create(self, validated_data):
		try:
			with transaction.atomic():
				rate_of_demostration = validated_data.pop('rate_of_demostration')
				rate_experince_in_operating_room = validated_data.pop('rate_experince_in_operating_room')
				rate_hospital_facility = validated_data.pop('rate_hospital_facility')
				rate_of_experince_overall = validated_data.pop('rate_of_experince_overall')
				rate_level_of_training = validated_data.pop('rate_level_of_training')
				rate_corcym_support = validated_data.pop('rate_corcym_support')
				preceptor_ship_feedback = PreceptorshipTraineeUploads.objects.create(**validated_data)
				preceptor_ship_feedback.rate_of_demostration = Rating.objects.get(code = rate_of_demostration)
				preceptor_ship_feedback.rate_experince_in_operating_room = Rating.objects.get(code=rate_experince_in_operating_room)
				preceptor_ship_feedback.rate_hospital_facility = Rating.objects.get(code=rate_hospital_facility)
				preceptor_ship_feedback.rate_of_experince_overall = Rating.objects.get(code=rate_of_experince_overall)
				preceptor_ship_feedback.rate_level_of_training = Rating.objects.get(code=rate_level_of_training)
				preceptor_ship_feedback.rate_corcym_support = Rating.objects.get(code=rate_corcym_support)
				preceptor_ship_feedback.save()
				return preceptor_ship_feedback
		except Exception as e:
			return e



class PreceptorshipTraineeUpdateUploadsSerializers(serializers.ModelSerializer):
	rate_of_demostration = serializers.CharField(required=False)
	rate_experince_in_operating_room = serializers.CharField(required=False)
	rate_hospital_facility = serializers.CharField(required=False)
	number_of_patients = serializers.IntegerField(required=False)
	number_of_perceval = serializers.IntegerField(write_only=False)
	rate_of_experince_overall = serializers.CharField(required=False)
	rate_level_of_training = serializers.CharField(required=False)
	are_intrested_learning_more = serializers.BooleanField(required=False)
	rate_corcym_support = serializers.CharField(required=False)
	corcym_suggestion = serializers.CharField(required=False)
	proctor_report = serializers.FileField(required=False)
	class Meta:
		model = PreceptorshipTraineeUploads
		fields = ['rate_of_demostration','rate_experince_in_operating_room','rate_hospital_facility','number_of_patients', 'number_of_perceval', 'rate_of_experince_overall', 'rate_level_of_training', 'are_intrested_learning_more','rate_corcym_support', 'proctor_report', 'corcym_suggestion']

	def update(self, instance, validated_data):
		try:
			if 'rate_of_demostration' in validated_data.keys():
				rate_of_demostration = validated_data.pop('rate_of_demostration')
				validated_data['rate_of_demostration'] = Rating.objects.get(code = rate_of_demostration)
				instance.rate_of_demostration = validated_data.get('rate_of_demostration', instance.rate_of_demostration)

			if 'rate_experince_in_operating_room' in validated_data.keys():
				rate_experince_in_operating_room = validated_data.pop('rate_experince_in_operating_room')
				validated_data['rate_experince_in_operating_room'] = Rating.objects.get(code=rate_experince_in_operating_room)
				instance.rate_experince_in_operating_room = validated_data.get('rate_experince_in_operating_room',
																   instance.rate_experince_in_operating_room)

			if 'rate_hospital_facility' in validated_data.keys():
				rate_hospital_facility = validated_data.pop('rate_hospital_facility')
				validated_data['rate_hospital_facility'] = Rating.objects.get(code=rate_hospital_facility)
				instance.rate_hospital_facility = validated_data.get('rate_hospital_facility',
																   instance.rate_hospital_facility)

			if 'rate_of_experince_overall' in validated_data.keys():
				rate_of_experince_overall = validated_data.pop('rate_of_experince_overall')
				validated_data['rate_of_experince_overall'] = Rating.objects.get(code=rate_of_experince_overall)
				instance.rate_of_experince_overall = validated_data.get('rate_of_experince_overall',
																   instance.rate_of_experince_overall)

			if 'rate_level_of_training' in validated_data.keys():
				rate_level_of_training = validated_data.pop('rate_level_of_training')
				validated_data['rate_level_of_training'] = Rating.objects.get(code=rate_level_of_training)
				instance.rate_level_of_training = validated_data.get('rate_level_of_training',
																   instance.rate_level_of_training)

			if 'rate_corcym_support' in validated_data.keys():
				rate_corcym_support = validated_data.pop('rate_corcym_support')
				validated_data['rate_corcym_support'] = Rating.objects.get(code=rate_corcym_support)
				instance.rate_corcym_support = validated_data.get('rate_corcym_support',
																   instance.rate_corcym_support)

			instance.number_of_patients = validated_data.get('number_of_patients', instance.number_of_patients)
			instance.number_of_perceval =  validated_data.get('number_of_perceval', instance.number_of_perceval)
			instance.are_intrested_learning_more = validated_data.get('are_intrested_learning_more', instance.are_intrested_learning_more)
			instance.corcym_suggestion = validated_data.get('corcym_suggestion', instance.corcym_suggestion)

			if 'proctor_report' in validated_data.keys():
				instance.proctor_report =  validated_data.get('proctor_report', instance.proctor_report)

			instance.save()
			return instance
		except Exception as e:
			return e

class PProposalDateUpdateSerializer(serializers.ModelSerializer):
	start_date = serializers.DateField(required=True)
	end_date = serializers.DateField(required=True)
	class Meta:
		model = PreceptorshipProposal
		fields = ['start_date', 'end_date']

	def update(self, instance, validated_data):
		try:
			instance.start_date = validated_data.get('start_date', instance.start_date)
			instance.end_date = validated_data.get('end_date', instance.end_date)
			instance.save()
			return instance
		except Exception as e:
			return e


class PreceptorshipViewListingSerializer(serializers.ModelSerializer):
	user = serializers.SerializerMethodField(read_only=True)
	is_global = serializers.BooleanField(read_only=True)
	product = serializers.SerializerMethodField(read_only=True)
	secondary_product = serializers.SerializerMethodField(read_only=True)
	hospital = serializers.SerializerMethodField(read_only=True)
	note = serializers.CharField(read_only=True)
	training_type = serializers.CharField(read_only=True)
	types_of_first_training = serializers.CharField(read_only = True)
	type_advance_training = serializers.CharField(read_only=True)
	specific_training = serializers.CharField(read_only=True)
	not_implant_regularly = serializers.CharField(read_only=True)
	status = serializers.SerializerMethodField(read_only=True)
	rem_seats = serializers.SerializerMethodField(read_only=True)
	proctor = serializers.SerializerMethodField(read_only=True)
	date = serializers.SerializerMethodField(read_only=True)
	cognos_id = serializers.SerializerMethodField(read_only=True)
	activity_id = serializers.CharField(read_only=True)
	class Meta:
		model = Preceptorship
		fields = ['id',"activity_id","user", "is_global", "product","secondary_product", "hospital", "note", "training_type", "types_of_first_training",
				  "type_advance_training", "specific_training","status","not_implant_regularly", "rem_seats", "proctor", 'date', 'cognos_id']
		# fields = "__all__"
	def get_user(self, obj):
		try:
			return obj.user.name
		except:
			return None

	def get_country(self, obj):
		try:
			return obj.country.name
		except:
			return None

	def get_hospital(self, obj):
		try:
			return obj.hospital.hospital_name
		except:
			return None

	def get_secondary_product(self, obj):
		try:
			return obj.secondary_product.product_name
		except:
			return None

	def get_product(self, obj):
		try:
			return obj.product.product_name
		except:
			return None

	def get_status(self, obj):
		try:
			return PreceptorshipStatusViewSerializer(obj.preceptorshipStatus_status.latest('timestamp')).data['code']
		except:
			return None

	def get_proctor(self, obj):
		try:

			return PreceptorshipProctorsSerializer(obj.preceptorshipStatus_status.filter(alter_preceptorship_porposal__isnull=False).latest(
				'created_on').alter_preceptorship_porposal.filter(preceptorship_porposal__isnull=False).latest(
				'created_on').preceptorship_porposal.get(status = True)).data['proctors']
		except:
			return None

	def get_rem_seats(self, obj):
		try:
			hospital = obj.hospital.number_of_trainee
			traine = TraineePreceptorshipProfile.objects.filter(preceptorship__id=obj.id, revoke=False)
			rem = hospital - traine.count()
			if rem > 0:
				return rem
			else:
				return 0
		except:
			return None

	def get_date(self, obj):
		try:

			return obj.preceptorshipStatus_status.filter(alter_preceptorship_porposal__isnull=False).latest(
				'created_on').alter_preceptorship_porposal.get().start_date
		except:
			return None

	def get_cognos_id(self, obj):
		try:
			return obj.hospital.cognos_id
		except:
			return None


class InvoicePerceptorshipSerializer(serializers.ModelSerializer):
    preceptorship_id = serializers.IntegerField(write_only=True)
    invoice_number = serializers.CharField(required=True )
    fee_covered = serializers.CharField(required=True)
    other_cost = serializers.CharField(required=True)
    invoice_date = serializers.DateField(required=True)
    note = serializers.CharField(required=True, allow_null=True, allow_blank=True)
    invoice_sent = serializers.BooleanField(required=True, allow_null=True)
    class Meta:
        model = InvoicePerceptorship
        fields = ['preceptorship_id', 'invoice_number', 'fee_covered', 'other_cost', 'invoice_date', 'note', 'invoice_sent']

    def create(self, validated_data):
        try:
            with transaction.atomic():
                invoice = InvoicePerceptorship.objects.create(**validated_data)
                invoice.save()
                return invoice
        except Exception as e:
            return None



class AttendancePerceptorShipSerailizers(serializers.ModelSerializer):
    preceptorship_id = serializers.IntegerField(write_only=True)
    attendance_form = serializers.FileField(required=True)
    class Meta:
        model = AttendanceFormPerceptorship
        fields = ["id",'preceptorship_id',"attendance_form"]

    def create(self, validated_data):
        try:
            with transaction.atomic():
                attendace_form = AttendanceFormPerceptorship.objects.create(**validated_data)
                attendace_form.save()
                return attendace_form
        except Exception as e:
            return None

class PreceptorshipStatusTestingSerializer(serializers.ModelSerializer):
    status = serializers.CharField(required = True)
    perceptorship_activity_id = serializers.IntegerField(write_only=True)
    date = serializers.DateField(read_only=True)
    code = serializers.CharField(read_only=True)
    reason = serializers.CharField(required=False)

    class Meta:
        model = PreceptorshipStatus
        fields = ['id','status', 'reason','perceptorship_activity_id','code', 'date']

    def create(self, validated_data):
        try:
            with transaction.atomic():
                status = validated_data.pop('status')
                validated_data ['status'] = StatusConstantData.objects.get(code = status)
                status = PreceptorshipStatus.objects.create(**validated_data)
                status.save()
                return status
        except Exception as e:
            return e



class AttendanceFormPerceptorshipUpdateSerailizers(serializers.ModelSerializer):
    attendance_form = serializers.FileField(required=True)

    class Meta:
        model = AttendanceFormPerceptorship
        fields = ["id", "attendance_form"]
    def update(self, instance, validated_data):
        try:
            instance.attendance_form = validated_data.get('attendance_form', instance.attendance_form)
            instance.save()
            return instance
        except Exception as e:
            return e

class InvoicePerceptorshipUpdateSerializer(serializers.ModelSerializer):
    invoice_number = serializers.CharField(required=True )
    fee_covered = serializers.CharField(required=True)
    other_cost = serializers.CharField(required=True)
    invoice_date = serializers.DateField(required=True)
    note = serializers.CharField(required=True, allow_null=True, allow_blank=True)
    invoice_sent = serializers.BooleanField(required=True, allow_null=True)
    class Meta:
        model = InvoicePerceptorship
        fields = [ 'invoice_number', 'fee_covered', 'other_cost', 'invoice_date', 'note', 'invoice_sent']

    def update(self, instance, validated_data):
        try:
            instance.invoice_number = validated_data.get('invoice_number', instance.invoice_number)
            instance.fee_covered = validated_data.get('fee_covered', instance.fee_covered)
            instance.other_cost = validated_data.get('other_cost', instance.other_cost)
            instance.invoice_date = validated_data.get('invoice_date', instance.invoice_date)
            instance.note = validated_data.get('note', instance.note)
            instance.invoice_sent = validated_data.get('invoice_sent', instance.invoice_sent)
            instance.save()
            return instance
        except Exception as e:
            return e

