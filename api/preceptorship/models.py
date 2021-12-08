from django.db import models
from api.feedback.models import Rating, PercevelDriver
from api.models import Products, Hospital, Hcp_role
from api.proctors.models import Proctors
from api.proctorship.models import ConstantData
from api.status.models import StatusConstantData
from api.users.models import User
from api.zone.models import Countries, ZoneCountries, Zone
from main.models import Base
from django.utils import timezone


# Create your models here.


class Preceptorship(Base):
	user = models.ForeignKey(User,on_delete=models.CASCADE, related_name = "preceptorship_user", db_column= "PreceptorshipUserID")
	is_global = models.BooleanField(default=False, db_column='IsGlobal')
	product = models.ForeignKey(Products, db_column='ProductID', null=True, related_name="perceptorship_product",on_delete=models.CASCADE, default=None, )
	secondary_product = models.ForeignKey(Products, db_column='SecondaryProductID', null=True, related_name="perceptorship_secondary_product", on_delete=models.CASCADE,default=None)
	hospital = models.ForeignKey(Hospital, db_column="HospitalPreceptorshipID", null=True, blank=True,on_delete=models.CASCADE, related_name="preceptorship_hospital")
	note = models.TextField(db_column='Note')
	training_type = models.ForeignKey(ConstantData, db_column='TrainingType', related_name='preceptorship_training_Type_constantdata',default=None, null=True, blank=True, on_delete=models.CASCADE)
	types_of_first_training = models.ForeignKey(ConstantData, db_column='TypesOfFirstTraining', default=None,related_name='preceptorship_types_of_first_training_constantdata', null=True,blank=True, on_delete=models.CASCADE)
	type_advance_training = models.ForeignKey(ConstantData, related_name='preceptorship_type_advance_training_constantdata',on_delete=models.CASCADE, null=True, blank=True, default=None, db_column='TypesofAdvancedTraining')
	specific_training = models.ForeignKey(ConstantData, related_name='preceptorship_specific_training_constantdata', db_column='SpecificTraining', default=None, null=True, blank=True, on_delete=models.CASCADE)
	not_implant_regularly = models.ForeignKey(ConstantData, on_delete=models.CASCADE, db_column='NotImplantRegularly', default=None, related_name='preceptorship_not_implant_regularly_constantdata',null=True, blank=True)
	activity_id = models.CharField(db_column="ActivityID", default=None, null=True, blank=True, max_length = 255)
	zone = models.ForeignKey(Zone, on_delete=models.CASCADE, null=True,db_column='PerceptorshipZoneID', related_name='prceptors_zone_countries', default=None)

	class Meta:
		db_table = 'Preceptorship'






class TraineePreceptorshipProfile(Base):
	preceptorship = models.ForeignKey(Preceptorship, null= True, blank= True, on_delete=models.CASCADE, related_name = "trainee_preceptorship", db_column ='TraineePreceptorship', default = None )
	hospital =  models.ForeignKey(Hospital, db_column= "HospitalTraineePreceptorshipProfileID", null= True, blank= True, on_delete=models.CASCADE, related_name = "traineeprofile_preceptorship_hospital")
	country = models.ForeignKey(Countries, db_column = "CountriesTraineeProfileID",null= True, blank= True, on_delete=models.CASCADE, related_name = "traineeprofile_preceptorship_country")
	title = models.ForeignKey(ConstantData, default = None,related_name='preceptorship_title_constantdata',null=True, blank=True, db_column = "Title", on_delete=models.CASCADE)
	name = models.CharField(max_length = 255, default = "", db_column = "Name")
	surname = models.CharField(max_length = 255, default = "", db_column = "SurName")
	corcym_accompanying_rep = models.CharField(max_length = 255, db_column ='CorcymAccompanyingRep',  null = True, blank = True, default = "")
	current_preferential = models.ForeignKey(ConstantData, db_column = 'CurrentPreferential', default = None, related_name='preceptorship_current_preferential_constantdata', on_delete=models.CASCADE, blank=True, null=True)
	mvr_case_per_year = models.IntegerField(db_column= 'MVRCasePerYear')
	mvr_case_per_year_by_trainee = models.IntegerField(db_column = 'MVRCasePerYearByTrainee')
	note = models.TextField(db_column = 'Note')
	status = models.BooleanField(db_column = 'Status', default = False)
	revoke = models.BooleanField(db_column = 'Revoke', default = False)
	interest_invasive = models.BooleanField(default=False, db_column='InterestInvasive')
	class Meta:
		db_table = 'TraineePreceptorshipProfile'


class PreceptorshipStatus(Base):
	user = models.ForeignKey(User, db_column="UserId", default=None, related_name="preceptorship_status_user", on_delete=models.CASCADE,null = True)
	status = models.ForeignKey(StatusConstantData, related_name ='preceptorship_status_data' ,db_column='Status', default=None, null=True, on_delete=models.CASCADE)
	preceptorship_activity = models.ForeignKey(Preceptorship, db_column='PreceptorshipStatusId',related_name='preceptorshipStatus_status',default=None, null=True, blank=True, on_delete=models.CASCADE)
	date = models.DateField(auto_now_add=True, db_column='Date')
	timestamp = models.DateTimeField(default=timezone.now, db_column='TimeStamp')
	reason = models.CharField(default='', db_column='Reason', max_length=255, blank=True, null = True)
	is_active = models.BooleanField(default=True, db_column='IsActive')

	class Meta:
		db_table = 'PreceptorshipStatus'


class PreceptorshipProposal(Base):
	status = models.ForeignKey(PreceptorshipStatus, db_column='StatusId', related_name= 'alter_preceptorship_porposal',default=None, null=True,blank=True, on_delete=models.CASCADE)
	note = models.TextField(db_column='Note', default='')
	start_date = models.DateField(auto_now=False, db_column='StartDate', auto_now_add=False, default=None)
	end_date = models.DateField(auto_now=False, db_column='EndDate', auto_now_add=False, default=False)
	class Meta:
		db_table = 'PreceptorshipProposal'

class PreceptorshipProctors(Base):
	preceptorship_proposal = models.ForeignKey(PreceptorshipProposal, on_delete=models.CASCADE, db_column='PreceptorshipPorposalID', related_name='preceptorship_porposal', null=True)
	proctors = models.ForeignKey(Proctors, on_delete=models.CASCADE, db_column='ProctorsID',related_name='Preceptorship_proctor_data', null=True)
	status = models.BooleanField(default=True, db_column='PreceptorshipProctorStatus')
	class Meta:
		db_table = 'PreceptorshipProctors'


class PreceptorshipTraineeUploads(Base):
	preceptorship_trainee = models.ForeignKey(TraineePreceptorshipProfile, null= True, blank= True, on_delete=models.CASCADE, related_name = "feedback_preceptorship_trainee", db_column ='TraineePreceptorship', default = None )
	rate_of_demostration = models.ForeignKey(Rating, db_column='RteOfostration',related_name='rate_of_demostration_rating', default=None, null=True,on_delete=models.CASCADE)
	rate_experince_in_operating_room = models.ForeignKey(Rating, db_column='RateOfExperinceInOperatingRoom',related_name='rate_experince_in_operating_room_rating',default=None, null=True, on_delete=models.CASCADE)
	rate_hospital_facility = models.ForeignKey(Rating, db_column='RateOfFacility', related_name='rate_hospital_facility_rating', default=None, null=True,on_delete=models.CASCADE)
	number_of_patients = models.IntegerField(db_column='NumberOfPatients', default = None)
	number_of_perceval = models.IntegerField(db_column='NumberOfPerceval', default = None)
	rate_of_experince_overall = models.ForeignKey(Rating, db_column='OverallExperince',related_name='overall_experince_rating',default=None, null=True, on_delete=models.CASCADE)
	percevel_driver = models.CharField(max_length = 255, db_column='PercevelDriverId', null=True, blank=True)
	rate_level_of_training = models.ForeignKey(Rating, db_column='RateLevlOfTrainig',related_name='rate_level_of_training_rating',default=None, null=True, on_delete=models.CASCADE)
	are_intrested_learning_more = models.BooleanField(db_column = 'IntrestedInLearningMore', default = False)
	rate_corcym_support = models.ForeignKey(Rating, db_column='RateCorcymSupport', related_name='rate_corcym_support_rating', default=None, null=True,on_delete=models.CASCADE)
	corcym_suggestion = models.TextField(db_column='CorcymSuggestions',default='', null=True, blank=True)
	proctor_report = models.FileField(db_column='PreceptorReport', upload_to='uploads/', null=True, blank=True, default=None)
	is_memo_family = models.BooleanField(db_column='IsMemoFmaily', default=False)
	is_perceval = models.BooleanField(db_column='IsPerceval', default=False)
	is_solo_smart = models.BooleanField(db_column='IsSoloSmart', default=False)
	class Meta:
		db_table = 'PreceptorshipTraineeUploads'


# class PreceptorshipTraineeMemoFamilyUploads(Base):
#   preceptorship = models.ForeignKey(Preceptorship, null= True, blank= True, on_delete=models.CASCADE, related_name = "feedback_memo_preceptorship", db_column ='TraineePreceptorship', default = None )
#   rate_of_demostration = models.ForeignKey(Rating, db_column='RteOfDemonstration',related_name='rate_of_demostration_memofamily', default=None, null=True,on_delete=models.CASCADE)
#   rate_experince_in_operating_room = models.ForeignKey(Rating, db_column='RateOfExperinceInOperatingRoom',related_name='rate_experince_in_operating_room_memo_family_rating',default=None, null=True, on_delete=models.CASCADE)
#   rate_hospital_facility = models.ForeignKey(Rating, db_column='RateOfFacility', related_name='rate_hospital_facility_memo_rating', default=None, null=True,on_delete=models.CASCADE)
#   number_of_patients = models.IntegerField(db_column='NumberOfPatients', default = None)
#   number_of_perceval = models.IntegerField(db_column='NumberOfPerceval', default = None)
#   rate_of_experince_overall = models.ForeignKey(Rating, db_column='OverallExperince',related_name='overall_experince_memo_rating',default=None, null=True, on_delete=models.CASCADE)
#   rate_level_of_training = models.ForeignKey(Rating, db_column='RateLevlOfTrainig',related_name='rate_level_of_memo_training_rating',default=None, null=True, on_delete=models.CASCADE)
#   are_intrested_learning_more = models.BooleanField(db_column = 'IntrestedInLearningMore', default = False)
#   rate_corcym_support = models.ForeignKey(Rating, db_column='RateCorcymSupport', related_name='rate_corcym_memo_support_rating', default=None, null=True,on_delete=models.CASCADE)
#   corcym_suggestion = models.TextField(db_column='CorcymSuggestions',default='', null=True, blank=True)
#   proctor_report = models.FileField(db_column='PreceptorMemoReport', upload_to='uploads/', null=True, blank=True, default=None)
#   class Meta:
#       db_table = 'PreceptorshipTraineeMemoFamilyUploads'


# class PreceptorshipTraineeSoloSmartUploads(Base):
#   preceptorship = models.ForeignKey(Preceptorship, null= True, blank= True, on_delete=models.CASCADE, related_name = "feedback_solo_preceptorship", db_column ='TraineePreceptorship', default = None )
#   rate_of_demostration = models.ForeignKey(Rating, db_column='RteOfDemonstration',related_name='rate_of_demostration_solo', default=None, null=True,on_delete=models.CASCADE)
#   rate_experince_in_operating_room = models.ForeignKey(Rating, db_column='RateOfExperinceInOperatingRoom',related_name='rate_experince_in_operating_room_solo_rating',default=None, null=True, on_delete=models.CASCADE)
#   rate_hospital_facility = models.ForeignKey(Rating, db_column='RateOfFacility', related_name='rate_hospital_facility_solo_rating', default=None, null=True,on_delete=models.CASCADE)
#   number_of_patients = models.IntegerField(db_column='NumberOfPatients', default = None)
#   number_of_perceval = models.IntegerField(db_column='NumberOfPerceval', default = None)
#   rate_of_experince_overall = models.ForeignKey(Rating, db_column='OverallExperince',related_name='overall_experince_solo_rating',default=None, null=True, on_delete=models.CASCADE)
#   rate_level_of_training = models.ForeignKey(Rating, db_column='RateLevlOfTrainig',related_name='rate_level_of_solo_training_rating',default=None, null=True, on_delete=models.CASCADE)
#   are_intrested_learning_more = models.BooleanField(db_column = 'IntrestedInLearningMore', default = False)
#   rate_corcym_support = models.ForeignKey(Rating, db_column='RateCorcymSupport', related_name='rate_corcym_solo_support_rating', default=None, null=True,on_delete=models.CASCADE)
#   corcym_suggestion = models.TextField(db_column='CorcymSuggestions',default='', null=True, blank=True)
#   proctor_report = models.FileField(db_column='PreceptorSoloReport', upload_to='uploads/', null=True, blank=True, default=None)
#   class Meta:
#       db_table = 'PreceptorshipTraineeSoloSmartUploads'


class InvoicePerceptorship(Base):
	preceptorship = models.ForeignKey(Preceptorship, on_delete=models.CASCADE, related_name='preceptorship_invoice', db_column='PreceptorshipID', default=None, null = True)
	invoice_number = models.CharField(db_column='InvoiceNumber', default=None, max_length=255, blank=True, null=True)
	fee_covered = models.CharField(db_column='FEECoveredbyMedicalAffair', default='', max_length=255)
	other_cost =models.CharField(db_column='OtherCostsCoveredByMedicalAffair', default='', max_length=255)
	invoice_date = models.DateField(db_column='DateOfInvoice', default=None)
	note = models.TextField(db_column='Note', default='')
	invoice_sent = models.BooleanField(db_column='InvoicesSentToTheAdministration', default=False)
	class Meta:
		db_table = 'InvoicePerceptorship'

class AttendanceFormPerceptorship(Base):
	attendance_form = models.FileField(db_column='AttendanceForm', upload_to='uploads/', null=True,
												blank=True, default=None)
	preceptorship = models.ForeignKey(Preceptorship, on_delete=models.CASCADE, related_name='preceptorship_attendance_form',
									  db_column='PreceptorshipID', default=None, null=True)
	class Meta:
		db_table = "AttendanceFormPerceptorship"

