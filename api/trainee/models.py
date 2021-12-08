from django.db import models
from api.users.models import User
from api.zone.models import Countries
from api.models import Products, Hospital, Hcp_role
from api.proctorship.models import Proctorship
from main.models import Base
from api.users.models import User
from api.proctorship.models import ConstantData

# Create your models here.

class TraineeProfile(Base):
	proctorship = models.ForeignKey(Proctorship, null= True, blank= True, on_delete=models.CASCADE, related_name = "trainee_proctorship", db_column ='TraineeProctorship', default = None )
	hospital =  models.ForeignKey(Hospital, db_column= "HospitalTraineeProfileID", null= True, blank= True, on_delete=models.CASCADE, related_name = "traineeprofile_hospital")
	country = models.ForeignKey(Countries, db_column = "CountriesTraineeProfileID",null= True, blank= True, on_delete=models.CASCADE, related_name = "traineeprofile_country")
	title = models.ForeignKey(ConstantData, default = None,related_name='title_constantdata',null=True, blank=True, db_column = "Title", on_delete=models.CASCADE)
	name = models.CharField(max_length = 255, default = "", db_column = "Name")
	surname = models.CharField(max_length = 255, default = "", db_column = "SurName")
	corcym_accompanying_rep = models.CharField(max_length = 255, db_column ='CorcymAccompanyingRep',  null = True, blank = True, default = "")
	current_preferential = models.ForeignKey(ConstantData, db_column = 'CurrentPreferential', default = None, related_name='current_preferential_constantdata', on_delete=models.CASCADE, blank=True, null=True)
	mvr_case_per_year = models.IntegerField(db_column= 'MVRCasePerYear')
	mvr_case_per_year_by_trainee = models.IntegerField(db_column = 'MVRCasePerYearByTrainee')
	note = models.TextField(db_column = 'Note')
	status = models.BooleanField(db_column = 'Status', default = False)
	revoke = models.BooleanField(db_column = 'Revoke', default = False)
	interest_invasive = models.BooleanField(default=False, db_column='InterestInvasive')

	class Meta:
		db_table = 'TraineeProfile'