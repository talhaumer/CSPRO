from django.db import models
from django.utils import timezone

from api.feedback.models import Reason, Rating
from api.models import Products, Hospital
from api.preceptorship.models import Preceptorship
from api.proctors.models import Proctors
from api.proctorship.models import ConstantData
from api.status.models import StatusConstantData
from api.users.models import User
from api.zone.models import Countries
from main.models import Base


class NewMics(Base):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="mics_user",
                             db_column="MicsUserID")
    is_rat = models.BooleanField(default=False, db_column="TypeOfMics")

    class Meta:
        db_table = "NewMics"


class MicsPreceptorship(Base):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="mics_preceptorship_user",
                             db_column="MicsPreceptorshipUserID")
    product = models.ForeignKey(Products, db_column='ProductID', null=True, related_name="mics_perceptorship_product",
                                on_delete=models.CASCADE, default=None, )
    hospital = models.ForeignKey(Hospital, db_column="HospitalMicsPreceptorshipID", null=True, blank=True,
                                 on_delete=models.CASCADE, related_name="mics_preceptorship_hospital")
    note = models.TextField(db_column='Note')
    mics = models.ForeignKey(NewMics, on_delete=models.CASCADE, related_name="mics_perceptotship", null=True,
                             blank=True, db_column="MicsCourseId")

    class Meta:
        db_table = 'MicsPreceptorship'


    def close_perceptership(self):
        if  self.mics_attendance_form_mics_perceptership.count() > 0 and\
                self.mics.mics_traineeprofile.filter(revoke=False).count() == self.mics_trainee_feedback_mics_perceptership.filter(trainee__revoke=False).count() and \
                self.mics_preceptorshipStatus_status.all().order_by("-id")[0].status.code != 'closed':

            self.mics_preceptorshipStatus_status.all().update(is_active=False)
            obj = {}
            obj['mics_preceptorship_activity'] = self
            obj['status'] = StatusConstantData.objects.get(code='closed')
            status = MicsPreceptorshipStatus.objects.create(**obj)

class MicsPreceptorshipStatus(Base):
    user = models.ForeignKey(User, db_column="UserId", default=None, related_name="mics_preceptorship_status_user",
                             on_delete=models.CASCADE, null=True)
    status = models.ForeignKey(StatusConstantData, related_name='mics_preceptorship_status_data', db_column='Status',
                               default=None, null=True, on_delete=models.CASCADE)
    mics_preceptorship_activity = models.ForeignKey(MicsPreceptorship, db_column='MicsPreceptorshipStatusId',
                                               related_name='mics_preceptorshipStatus_status', default=None, null=True,
                                               blank=True, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True, db_column='Date')
    timestamp = models.DateTimeField(default=timezone.now, db_column='TimeStamp')
    reason = models.CharField(default='', db_column='Reason', max_length=255, blank=True, null=True)
    is_active = models.BooleanField(default=True, db_column='IsActive')

    class Meta:
        db_table = 'MicsPreceptorshipStatus'


class MicsPreceptorshipProposal(Base):
    status = models.ForeignKey(MicsPreceptorshipStatus, db_column='StatusId',
                               related_name='alter_mics_preceptorship_porposal', default=None, null=True, blank=True,
                               on_delete=models.CASCADE)
    note = models.TextField(db_column='Note', default='')
    start_date = models.DateField(auto_now=False, db_column='StartDate', auto_now_add=False, default=None)
    end_date = models.DateField(auto_now=False, db_column='EndDate', auto_now_add=False, default=False)

    class Meta:
        db_table = 'MicsPreceptorshipProposal'


class MicsPreceptorshipProctors(Base):
    mics_preceptorship_proposal = models.ForeignKey(MicsPreceptorshipProposal, on_delete=models.CASCADE,
                                                    db_column='PreceptorshipPorposalID',
                                                    related_name='mics_preceptorship_porposal', null=True)
    proctors = models.ForeignKey(Proctors, on_delete=models.CASCADE, db_column='ProctorsID',
                                 related_name='mics_preceptorship_proctor_data', null=True)
    status = models.BooleanField(default=True, db_column='PreceptorshipProctorStatus')

    class Meta:
        db_table = 'MicsPreceptorshipProctors'


class MicsProctorship(Base):
    mics = models.ForeignKey(NewMics, on_delete=models.CASCADE, related_name="mics_peroctorship", null=True, blank=True,
                             db_column="MicsCourseId")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="mics_proctorship_user",
                             db_column="ProctorshipUserID")
    country = models.ForeignKey(Countries, db_column="CountriesProctorshipID", null=True, on_delete=models.CASCADE,
                                related_name="mics_proctorship_country", default=None)
    hospital = models.ForeignKey(Hospital, db_column="HospitalProctorshipID", null=True, on_delete=models.CASCADE,
                                 related_name="mics_proctorship_hospital", default=None)
    hotel = models.CharField(max_length=255, db_column='HotelName', default='', )
    number_of_cases = models.IntegerField(db_column="NumberOfCases", default=None, null=True, blank=True)
    transplant_time = models.CharField(db_column='TransplantTime', max_length=255, blank=True, null=True, default='')
    is_second = models.BooleanField(default=False, db_column='IsSecondProctorship')
    is_active = models.BooleanField(default=True, db_column='IsActive')


    class Meta:
        db_table = 'MicsProctorship'


    def close_proctorship(self):
        if  self.mics_attendance_form_mics_proctorship.count() > 0 and\
                self.mics_perceval_feedback_mics_proctorship.count() > 0 and\
                self.mics_invoice_mics_proctorship.count() >0 and\
                self.mics.mics_traineeprofile.filter(revoke=False).count() == self.mics_trainee_feedback_mics_proctorship.filter(trainee__revoke=False).count() and \
                self.mics_proctorship_status.all().order_by("-id")[0].status.code != 'closed':
            self.mics_proctorship_status.all().update(is_active=False)
            obj = {}
            obj['proctorship_activity'] = self
            obj['status'] = StatusConstantData.objects.get(code='closed')
            status = MicsProctorshipStatus.objects.create(**obj)


class MicsProctorshipStatus(Base):
    user = models.ForeignKey(User, db_column="UserId", default=None, related_name="mics_proctorship_status_user",
                             on_delete=models.CASCADE, null=True)
    status = models.ForeignKey(StatusConstantData, related_name='mics_proctorship_status_data', db_column='Status',
                               default=None, null=True, on_delete=models.CASCADE)
    proctorship_activity = models.ForeignKey(MicsProctorship, db_column='ProctorShipId',
                                             related_name='mics_proctorship_status', default=None, null=True,
                                             blank=True, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True, db_column='Date')
    timestamp = models.DateTimeField(default=timezone.now, db_column='TimeStamp')
    reason = models.CharField(default='', db_column='Reason', max_length=255, blank=True, null=True)
    is_active = models.BooleanField(default=True, db_column='IsActive')

    class Meta:
        db_table = 'MicsProctorshipStatus'


class MicsProctorshipProposal(Base):
    status = models.ForeignKey(MicsProctorshipStatus, db_column='StatusId', related_name='mics_proctorship_porposal',
                               default=None, null=True, blank=True, on_delete=models.CASCADE)
    note = models.TextField(db_column='Note', default='')
    start_date = models.DateField(auto_now=False, db_column='StartDate', auto_now_add=False, default=None)
    end_date = models.DateField(auto_now=False, db_column='EndDate', auto_now_add=False, default=False)

    class Meta:
        db_table = 'MicsProctorshipProposal'


class MicsProctorshipProctors(Base):
    porposal = models.ForeignKey(MicsProctorshipProposal, on_delete=models.CASCADE, db_column='PorposalID',
                                 related_name='mics_proctor_porposal', null=True)
    proctors = models.ForeignKey(Proctors, on_delete=models.CASCADE, db_column='ProctorsID',
                                 related_name='mics_porposal_proctor_id', null=True)
    status = models.BooleanField(default=True, db_column='ProctorshipProctorStatus')
    proctor_order = models.IntegerField(db_column='Order', default=None, null=True)

    class Meta:
        db_table = 'MicsProctorshipProctors'


class MicsTraineeProfile(Base):
    mics = models.ForeignKey(NewMics, on_delete=models.CASCADE, related_name="mics_traineeprofile", null=True,
                             blank=True, db_column="MicsCourseId")
    hospital = models.ForeignKey(Hospital, db_column="HospitalTraineeProfileID", null=True, blank=True,
                                 on_delete=models.CASCADE, related_name="mics_traineeprofile_hospital")
    country = models.ForeignKey(Countries, db_column="CountriesTraineeProfileID", null=True, blank=True,
                                on_delete=models.CASCADE, related_name="mics_traineeprofile_country")
    title = models.ForeignKey(ConstantData, default=None, related_name='mics_title_constantdata', null=True, blank=True,
                              db_column="Title", on_delete=models.CASCADE)
    name = models.CharField(max_length=255, default="", db_column="Name")
    surname = models.CharField(max_length=255, default="", db_column="SurName")
    corcym_accompanying_rep = models.CharField(max_length=255, db_column='CorcymAccompanyingRep', null=True, blank=True,
                                               default="")
    current_preferential = models.ForeignKey(ConstantData, db_column='CurrentPreferential', default=None,
                                             related_name='mics_current_preferential_constantdata',
                                             on_delete=models.CASCADE, blank=True, null=True)
    mvr_case_per_year = models.IntegerField(db_column='MVRCasePerYear')
    mvr_case_per_year_by_trainee = models.IntegerField(db_column='MVRCasePerYearByTrainee')
    note = models.TextField(db_column='Note')
    status = models.BooleanField(db_column='Status', default=False)
    revoke = models.BooleanField(db_column='Revoke', default=False)
    interest_invasive = models.BooleanField(default=False, db_column='InterestInvasive')

    class Meta:
        db_table = 'MicsTraineeProfile'


class MicsPercevalFeedback(Base):
    mics_perceptership = models.ForeignKey(MicsPreceptorship,db_column='MicsPerceptershipID', related_name='mics_perceval_feedback_mics_perceptership',default=None, null=True, on_delete=models.CASCADE)
    mics_proctorship = models.ForeignKey(MicsProctorship,db_column='MicsProctorshipID', related_name='mics_perceval_feedback_mics_proctorship',default=None, null=True, on_delete=models.CASCADE)
    # proctorship = models.ForeignKey(Proctorship,db_column='ProctorshipId', related_name='proctor_feedback_proctorship',default=None, null=True, on_delete=models.CASCADE)
    num_of_patients = models.IntegerField(db_column='NumberOfPatients', null=True, default=None)
    is_advance = models.BooleanField(default=False, db_column='IsPateintDataAdvance')
    implanted_patient =  models.IntegerField(db_column='NumberOfPatientOperated', default=None, null=True )
    implanted_perceval = models.IntegerField(db_column='NumberOfPercevalImplanted', default=None, null=True)
    reason_low_num_patients = models.ForeignKey(Reason,db_column='IfNumberOfPatientIsLowReason', related_name='mics_perceval_feedback_reason',default=None, null=True, on_delete=models.CASCADE)
    rate_of_experince = models.ForeignKey(Rating, db_column='RateOfExperinceOfProctorship', related_name='mics_perceval_feedback_rating',default=None, null=True, on_delete=models.CASCADE)
    is_trainee_implant = models.BooleanField(db_column='IsTraineeImplantWithOutProctor', default=False)
    any_leason = models.TextField(db_column='AnyLeasonThatYouWantToShare')
    report = models.FileField(upload_to ='uploads/', db_column = "ProctorReport", null = True, blank = True)

    class Meta:
        db_table = 'MicsPercevalFeedback'


class MicsTraineeFeedback(Base):
    # proctorship = models.ForeignKey(Proctorship, db_column='ProctorshipId', related_name='trainee_feedback_proctorship',default=None, null=True, on_delete=models.CASCADE)
    # trainee = models.ForeignKey(TraineeProfile,on_delete=models.CASCADE, related_name='trianee_feedback_id', db_column='TraineeFeedbackid', null=True )
    mics_perceptership = models.ForeignKey(MicsPreceptorship, db_column='MicsPerceptershipID',
                                           related_name='mics_trainee_feedback_mics_perceptership', default=None,
                                           null=True, on_delete=models.CASCADE)
    mics_proctorship = models.ForeignKey(MicsProctorship, db_column='MicsProctorshipID',
                                         related_name='mics_trainee_feedback_mics_proctorship', default=None,
                                         null=True, on_delete=models.CASCADE)

    trainee = models.ForeignKey(MicsTraineeProfile, db_column='MicsTraineeProfileID',
                                         related_name='mics_trainee_feedback_mics_trainee_profile', default=None,
                                         null=True, on_delete=models.CASCADE)
    implanted_perceval = models.IntegerField(db_column='NumberOfPercevalImplanted', default=None, null=True)
    number_patient = models.IntegerField(db_column='NumberOfPatient', default=None, null  =True)
    rate_of_experince = models.ForeignKey(Rating, db_column='RateOfExperinceOfProctorship', related_name='mics_trainee_feedback_experince', default=None, null=True,on_delete=models.CASCADE)
    rate_of_training = models.ForeignKey(Rating, db_column='RateOfTrainingOfProctorship',related_name='mics_trainee_feedback_training_rating', default=None, null=True,on_delete=models.CASCADE)
    need_further_training = models.BooleanField(db_column='DoYouFeelNeedFurtherTraining', default=False)
    plan_for_next = models.CharField(db_column='PlanForNext',max_length=255, default='', null = True, blank=True )
    any_sugestion = models.CharField(db_column="AnySuggestionForCorcym", max_length=255, default='', null = True, blank=True)
    report = models.FileField(upload_to='uploads/', db_column="TraineeReport", null=True, blank=True)
    is_memo_family = models.BooleanField(db_column='IsMemoFmaily', default=False)
    is_perceval = models.BooleanField(db_column='IsPerceval', default=False)
    is_solo_smart = models.BooleanField(db_column='IsSoloSmart', default=False)
    perceval_driver = models.CharField(db_column='KeyDriverForPerceval', default='', max_length=255, blank=True, null=True)

    class Meta:
        db_table = 'MicsTraineeFeedback'



class MicsInvoice(Base):
    mics_perceptership = models.ForeignKey(MicsPreceptorship, db_column='MicsPerceptershipID',
                                           related_name='mics_invoice_mics_perceptership', default=None,
                                           null=True, on_delete=models.CASCADE)
    mics_proctorship = models.ForeignKey(MicsProctorship, db_column='MicsProctorshipID',
                                         related_name='mics_invoice_mics_proctorship', default=None,
                                         null=True, on_delete=models.CASCADE)
    invoice_number = models.CharField(db_column='InvoiceNumber', default=None, max_length=255, null=True, blank=True)
    fee_covered = models.CharField(db_column='FEECoveredbyMedicalAffair', default='', max_length=255)
    other_cost = models.CharField(db_column='OtherCostsCoveredByMedicalAffair', default='', max_length=255)
    invoice_date = models.DateField(db_column='DateOfInvoice', default=None)
    note = models.TextField(db_column='Note', default='')
    invoice_sent = models.BooleanField(db_column='InvoicesSentToTheAdministration', default=False)

    class Meta:
        db_table = 'MicsInvoice'


class MicsAttendanceForm(Base):
    attendance_form = models.FileField(db_column='AttendanceForm', upload_to='uploads/', null=True,
                                       blank=True, default=None)
    mics_perceptership = models.ForeignKey(MicsPreceptorship, db_column='MicsPerceptershipID',
                                           related_name='mics_attendance_form_mics_perceptership', default=None,
                                           null=True, on_delete=models.CASCADE)
    mics_proctorship = models.ForeignKey(MicsProctorship, db_column='MicsProctorshipID',
                                         related_name='mics_attendance_form_mics_proctorship', default=None,
                                         null=True, on_delete=models.CASCADE)

    class Meta:
        db_table = "MicsAttendanceForm"


class MicsProctorshipCertificateForm(Base):
    certificate = models.FileField(db_column='Certificate', upload_to='uploads/', null=True,
                                       blank=True, default=None)
    mics_perceptership = models.ForeignKey(MicsPreceptorship, db_column='MicsPerceptershipID',
                                           related_name='mics_certificate_form_mics_perceptership', default=None,
                                           null=True, on_delete=models.CASCADE)
    mics_proctorship = models.ForeignKey(MicsProctorship, db_column='MicsProctorshipID',
                                         related_name='mics_certificate_form_mics_proctorship', default=None,
                                         null=True, on_delete=models.CASCADE)

    class Meta:
        db_table = "MicsProctorshipCertificateForm"

