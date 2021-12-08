from django.db import models
from django.utils import timezone
from api.proctors.models import Proctors
from main.models import Base
from api.users.models import User
from api.proctorship.models import Proctorship
from django.utils.text import slugify

# Create your models here.
import  datetime

class StatusConstantData(Base):
	code = models.SlugField(db_column='Code',default='')
	name = models.CharField(max_length=255, db_column='Name', default='')
	# type = models.CharField(db_column='Type',max_length=255, default='')
	class Meta:
		db_table = 'StatusConstantData'

	def __str__(self):
		return self.name

	def save(self, *args, **kwargs):
		try:
			if not self.pk:
				self.code = slugify(self.name)
			super().save()
		except Exception:
			raise

class Status(Base):
    user = models.ForeignKey(User, db_column="UserId", default=None, related_name="status_user", on_delete=models.CASCADE,null = True)
    status = models.ForeignKey(StatusConstantData, related_name ='status_data' ,db_column='Status', default=None, null=True, on_delete=models.CASCADE)
    proctorship_activity = models.ForeignKey(Proctorship, db_column='ProctorShipId',related_name='proctorship_status',default=None, null=True, blank=True, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True, db_column='Date')
    timestamp = models.DateTimeField(default=timezone.now, db_column='TimeStamp')
    reason = models.CharField(default='', db_column='Reason', max_length=255, blank=True, null = True)
    is_active = models.BooleanField(default=True, db_column='IsActive')
    class Meta:
        db_table = 'Status'


class Proposal(Base):
    status = models.ForeignKey(Status, db_column='StatusId', related_name= 'alter_proctorship_porposal',default=None, null=True,blank=True, on_delete=models.CASCADE)
    note = models.TextField(db_column='Note', default='')
    start_date = models.DateField(auto_now=False, db_column='StartDate', auto_now_add=False, default=None)
    end_date = models.DateField(auto_now=False, db_column='EndDate', auto_now_add=False, default=False)
    class Meta:
        db_table = 'AlternativeProposal'


class ProctorshipProctors(Base):
	porposal = models.ForeignKey(Proposal, on_delete=models.CASCADE, db_column='PorposalID', related_name='proctor_porposal', null=True)
	proctors = models.ForeignKey(Proctors, on_delete=models.CASCADE, db_column='ProctorsID',related_name='porposal_proctor_id', null=True)
	status = models.BooleanField(default=True, db_column='ProctorshipProctorStatus')
	proctor_order = models.IntegerField(db_column='Order', default=None, null=True)

	class Meta:
		db_table = 'ProctorshipProctors'