from django.db import models
from django.utils import timezone
from django.utils.text import slugify

from api.feedback.models import Rating
from api.proctorship.models import ConstantData
from api.status.models import StatusConstantData
from api.users.models import User
from api.zone.models import Countries
from api.models import Hospital
from api.proctors.models import Proctors
from main.models import Base


# Create your models here.
class MasterProctorShipConstantData(Base):
    code = models.SlugField(db_column='Code', max_length=255,default='')
    name = models.CharField(max_length=255, db_column='Name', default='')

    # type = models.CharField(db_column='Type',max_length=255, default='')
    class Meta:
        db_table = 'MasterProctorShipConstantData'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        try:
            if not self.pk:
                self.code = slugify(self.name)
            super().save()
        except Exception:
            raise


class MasterProctorship(Base):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="masterproctorship_user",
                             db_column="MasterProctorshipID")
    master_proctorship_type = models.ForeignKey(MasterProctorShipConstantData, db_column='MasterProctorshipType', default=None, related_name='master_proctorship_constant', on_delete=models.CASCADE, null = True)
    reason = models.CharField(max_length=255, db_column='Reason', default='')
    note = models.TextField(db_column='Note')
    country = models.ForeignKey(Countries, db_column="MasterProctorshipCountriesID", null=True, blank=True,
                                on_delete=models.CASCADE, related_name="masterproctorship_country")
    hospital = models.ForeignKey(Hospital, db_column="MasterProctorshipHospitalID", null=True, blank=True,
                                 on_delete=models.CASCADE, related_name="masterproctorship_hospital")
    hotel = models.CharField(max_length=255, db_column='HotelName', default='')
    number_of_cases = models.IntegerField(db_column='NumberofCases')
    transplant_time = models.CharField(db_column='TransplantTime', max_length=255, default='')
    activity_id = models.CharField(db_column="ActivityID", default=None, null=True, blank=True, max_length = 255)

    class Meta:
        db_table = 'MasterProctorship'


class MasterProctorshipTraineeProfile(Base):
    master_proctorship = models.ForeignKey(MasterProctorship, null=True, blank=True, on_delete=models.CASCADE,
                                           related_name="trainee_master_proctorship",
                                           db_column='MasterProctorshipTraineeProfileId', default=None)
    country = models.ForeignKey(Countries, db_column="CountriesTraineeProfileID", null=True, blank=True,
                                on_delete=models.CASCADE, related_name="traineeprofile_master_proctorship_country")
    hospital = models.ForeignKey(Hospital, db_column="MasterProctorshipTraineeHospitalID", null=True, blank=True,
                                 on_delete=models.CASCADE, related_name="masterproctorship_trainee_hospital")
    title = models.ForeignKey(ConstantData, default=None, related_name='master_proctorship_title_constantdata',
                              null=True, blank=True, db_column="Title", on_delete=models.CASCADE)
    name = models.CharField(max_length=255, default="", db_column="Name")
    surname = models.CharField(max_length=255, default="", db_column="SurName")
    corcym_accompanying_rep = models.CharField(max_length=255, db_column='CorcymAccompanyingRep', null=True, blank=True,
                                               default="")
    current_preferential = models.ForeignKey(ConstantData, db_column='CurrentPreferential', default=None,
                                             related_name='master_proctorship_current_preferential_constantdata',
                                             on_delete=models.CASCADE, blank=True, null=True)
    mvr_case_per_year = models.IntegerField(db_column='MVRCasePerYear')
    mvr_case_per_year_by_trainee = models.IntegerField(db_column='MVRCasePerYearByTrainee')
    note = models.TextField(db_column='Note')
    status = models.BooleanField(db_column='Status', default=False)
    revoke = models.BooleanField(db_column='Revoke', default=False)
    interest_invasive = models.BooleanField(default=False, db_column='InterestInvasive')

    class Meta:
        db_table = 'MasterProctorshipTraineeProfile'


class MasterProctorshipStatus(Base):
    user = models.ForeignKey(User, db_column="UserId", default=None, related_name="master_proctorship_status_user",
                             on_delete=models.CASCADE, null=True)
    status = models.ForeignKey(StatusConstantData, related_name='master_proctorship_status_data', db_column='Status',
                               default=None, null=True, on_delete=models.CASCADE)
    master_proctorship_activity = models.ForeignKey(MasterProctorship, db_column='MasterProctorshipStatusId',
                                                    related_name='master_proctorship_status', default=None, null=True,
                                                    blank=True, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True, db_column='Date')
    timestamp = models.DateTimeField(default=timezone.now, db_column='TimeStamp')
    reason = models.CharField(default='', db_column='Reason', max_length=255, blank=True, null=True)
    is_active = models.BooleanField(default=True, db_column='IsActive')

    class Meta:
        db_table = 'MasterProctorshipStatus'


class MasterProctorshipProposal(Base):
    status = models.ForeignKey(MasterProctorshipStatus, db_column='StatusId',
                               related_name='alter_master_proctorship_porposal', default=None, null=True, blank=True,
                               on_delete=models.CASCADE)
    note = models.TextField(db_column='Note', default='')
    start_date = models.DateField(auto_now=False, db_column='StartDate', auto_now_add=False, default=None)
    end_date = models.DateField(auto_now=False, db_column='EndDate', auto_now_add=False, default=False)

    class Meta:
        db_table = 'MasterProctorshipProposal'


class MasterProctorshipProctors(Base):
    master_proctorship_proposal = models.ForeignKey(MasterProctorshipProposal, on_delete=models.CASCADE,
                                                    db_column='MasterProctorshipProposalID',
                                                    related_name='master_proctorship_porposal', null=True)
    proctors = models.ForeignKey(Proctors, on_delete=models.CASCADE, db_column='ProctorsID',
                                 related_name='master_proctorship_proctor_data', null=True)
    status = models.BooleanField(default=True, db_column='MasterProctorshipProposalStatus')
    note_related_to_proctor = models.TextField(db_column='NoteRelatedToProctor', default='')
    proctor_order = models.IntegerField(db_column='ProctorOrder', default=None)

    class Meta:
        db_table = 'MasterProctorshipProctors'


class MasterProctorshipFeedback(Base):
    master_proctorship_activity = models.ForeignKey(MasterProctorship, db_column='MasterProctorshipFeedBackId',
                                                    related_name='master_proctorship_feedback', default=None, null=True,
                                                    blank=True, on_delete=models.CASCADE)
    num_of_patients = models.IntegerField(db_column='HowManyOatientSelected', default=None)
    rate_of_proceduresc = models.CharField(db_column='RateOfProceduralStep', max_length=255, default='', null=True, blank=True)
    rate_proctoring_experince = models.ForeignKey(Rating, db_column='RateProctoringExperince',
                                                    related_name='rate_procotring_rating', default=None, null=True,
                                                    blank=True, on_delete=models.CASCADE)
    rate_of_level_support = models.ForeignKey(Rating, db_column='RateOflevelOfSupport',
                                                    related_name='rate_of_level_support_rating', default=None, null=True,
                                                    blank=True, on_delete=models.CASCADE)
    new_proctor_need_further_training =models.BooleanField(db_column='NewProctorNeedFurtherTraining', default=False)
    suggestion = models.CharField(db_column='Suggestions', max_length=255, default='', null=True, blank=True)
    report =models.FileField(db_column='FeedbackReport', upload_to ='uploads/', null = True, blank = True, default=None)
    class Meta:
        db_table = 'MasterProctorshipFeedback'
        

class MasterProctorshipProctorReport(Base):
    master_proctorship_trainee = models.ForeignKey(MasterProctorshipTraineeProfile, db_column='MasterProctorshipTraineeProfileId',
                                                    related_name='master_proctorship_trainee_report', default=None, null=True,
                                                    blank=True, on_delete=models.CASCADE)
    num_of_patients = models.IntegerField(db_column='NumberOfPatients', null=True, default=None)
    num_of_perceval = models.IntegerField(db_column='NumberOfPercvelImplant', null=True, default=None)
    rate_of_experince = models.ForeignKey(Rating, db_column='RateOfExperinceOfMaterProctorship',
                                          related_name='rate_of_experince_rating', default=None, null=True,
                                          on_delete=models.CASCADE)
    have_difficulties = models.BooleanField(db_column='HaveyoufeelanyDifficulty', default=False)
    need_for_further_training = models.BooleanField(db_column='DidYouFeelNeedForEurtherTraining', default=False)
    corcym_suggestion = models.TextField(db_column='CorcymSuggestions',default='', null=True, blank=True)
    proctor_report = models.FileField(db_column='ProctorReport', upload_to='uploads/', null=True, blank=True, default=None)
    class Meta:
        db_table = 'MasterProctorshipProctorReport'


class InvoiceMasterProctorShip(Base):
    master_proctorship = models.ForeignKey(MasterProctorship, on_delete=models.CASCADE, related_name='master_proctorship_invoice', db_column='MasterProctorShipID',null=True, default=None)
    invoice_number = models.CharField(db_column='InvoiceNumber', default=None, max_length=255, null=True, blank=True)
    fee_covered = models.CharField(db_column='FEECoveredbyMedicalAffair', default='', max_length=255)
    other_cost =models.CharField(db_column='OtherCostsCoveredByMedicalAffair', default='', max_length=255)
    invoice_date = models.DateField(db_column='DateOfInvoice', default=None)
    note = models.TextField(db_column='Note', default='')
    invoice_sent = models.BooleanField(db_column='InvoicesSentToTheAdministration', default=False)
    class Meta:
        db_table = 'InvoiceMasterProctorShip'

class AttendanceFormMasterProctorShip(Base):
    attendance_form = models.FileField(db_column='AttendanceForm', upload_to='uploads/', null=True,
                                                blank=True, default=None)
    master_proctorship = models.ForeignKey(MasterProctorship, on_delete=models.CASCADE, related_name='master_proctorship_attendace', db_column='MasterProctorShipID',null=True, default=None)
    class Meta:
        db_table = "AttendanceFormMasterProctorShip"
