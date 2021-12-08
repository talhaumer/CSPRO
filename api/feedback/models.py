from django.db import models
from django.utils.text import slugify

from api.proctorship.models import Proctorship
from api.trainee.models import TraineeProfile
from main.models import Base
# Create your models here.


class Reason(Base):
    code = models.SlugField(db_column='Code', default='', max_length=255)
    name = models.CharField(max_length=255, db_column='Name', default='')
    class Meta:
        db_table = 'Reason'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        try:
            if not self.pk:
                self.code = slugify(self.name)
            super().save()
        except Exception:
            raise


class Rating(Base):
    code = models.SlugField(db_column='Code', default='', max_length=255)
    name = models.CharField(max_length=255, db_column='Name', default='')

    # type = models.CharField(db_column='Type',max_length=255, default='')
    class Meta:
        db_table = 'Rating'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        try:
            if not self.pk:
                self.code = slugify(self.name)
            super().save()
        except Exception:
            raise

class PercevelDriver(Base):
    code = models.SlugField(db_column='Code', default='', max_length=255)
    name = models.CharField(max_length=255, db_column='Name', default='')

    # type = models.CharField(db_column='Type',max_length=255, default='')
    class Meta:
        db_table = 'PercevelDriver'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        try:
            if not self.pk:
                self.code = slugify(self.name)
            super().save()
        except Exception:
            raise


class ProctorshipProctorFeedback(Base):
    proctorship = models.ForeignKey(Proctorship,db_column='ProctorshipId', related_name='proctor_feedback_proctorship',default=None, null=True, on_delete=models.CASCADE)
    num_of_patients = models.IntegerField(db_column='NumberOfPatients', null=True, default=None)
    is_advance = models.BooleanField(default=False, db_column='IsPateintDataAdvance')
    implanted_patient =  models.IntegerField(db_column='NumberOfPatientOperated', default=None, null=True )
    implanted_perceval = models.IntegerField(db_column='NumberOfPercevalImplanted', default=None, null=True)
    reason_low_num_patients = models.ForeignKey(Reason,db_column='IfNumberOfPatientIsLowReason', related_name='proctor_feedback_reason',default=None, null=True, on_delete=models.CASCADE)
    rate_of_experince = models.ForeignKey(Rating, db_column='RateOfExperinceOfProctorship', related_name='proctor_feedback_rating',default=None, null=True, on_delete=models.CASCADE)
    is_trainee_implant = models.BooleanField(db_column='IsTraineeImplantWithOutProctor', default=False)
    any_leason = models.TextField(db_column='AnyLeasonThatYouWantToShare')
    report = models.FileField(upload_to ='uploads/', db_column = "ProctorReport", null = True, blank = True)

    class Meta:
        db_table = 'ProctorshipProctorFeedback'


class TraineeFeedback(Base):
    # proctorship = models.ForeignKey(Proctorship, db_column='ProctorshipId', related_name='trainee_feedback_proctorship',default=None, null=True, on_delete=models.CASCADE)
    trainee = models.ForeignKey(TraineeProfile,on_delete=models.CASCADE, related_name='trianee_feedback_id', db_column='TraineeFeedbackid', null=True )
    implanted_perceval = models.IntegerField(db_column='NumberOfPercevalImplanted', default=None, null=True)
    number_patient = models.IntegerField(db_column='NumberOfPatient', default=None, null  =True)
    rate_of_experince = models.ForeignKey(Rating, db_column='RateOfExperinceOfProctorship', related_name='trainee_feedback_experince', default=None, null=True,on_delete=models.CASCADE)
    rate_of_training = models.ForeignKey(Rating, db_column='RateOfTrainingOfProctorship',related_name='trainee_feedback_training_rating', default=None, null=True,on_delete=models.CASCADE)
    need_further_training = models.BooleanField(db_column='DoYouFeelNeedFurtherTraining', default=False)
    plan_for_next = models.CharField(db_column='PlanForNext',max_length=255, default='', null = True, blank=True )
    any_sugestion = models.CharField(db_column="AnySuggestionForCorcym", max_length=255, default='', null = True, blank=True)
    report = models.FileField(upload_to='uploads/', db_column="TraineeReport", null=True, blank=True)
    is_memo_family = models.BooleanField(db_column='IsMemoFmaily', default=False)
    is_perceval = models.BooleanField(db_column='IsPerceval', default=False)
    is_solo_smart = models.BooleanField(db_column='IsSoloSmart', default=False)
    perceval_driver = models.CharField(db_column='KeyDriverForPerceval', default='', max_length=255, blank=True, null=True)
    class Meta:
        db_table = 'TraineeFeedback'


class MemoProctorFeedBack(Base):
    proctorship = models.ForeignKey(Proctorship, db_column='ProctorshipId', related_name='proctor_memo_feedback_proctorship', default=None, null=True,on_delete=models.CASCADE)
    implanted_memo = models.IntegerField(db_column='NumberOfMemoImplanted', default=None, null=True)
    rate_of_experince = models.ForeignKey(Rating, db_column='RateOfExperinceOfMemoProctorship', related_name='proctor_memo_feedback_rating', default=None, null=True, on_delete=models.CASCADE)
    is_trainee_implant = models.BooleanField(db_column='IsTraineeImplantWithOutProctor', default=False)
    any_leason = models.TextField(db_column='AnyLeasonThatYouWantToShare')
    report = models.FileField(upload_to='uploads/', db_column="ProctorReport", null=True, blank=True)
    class Meta:
        db_table = 'MemoProctorFeedBack'


class SoloSmartProctorFeedBack(Base):
    proctorship = models.ForeignKey(Proctorship, db_column='ProctorshipId', related_name='proctor_solo_feedback_proctorship', default=None, null=True,on_delete=models.CASCADE)
    implanted_solo_smart = models.IntegerField(db_column='NumberOfMemoImplanted', default=None, null=True)
    rate_of_experince = models.ForeignKey(Rating, db_column='RateOfExperinceOfMemoProctorship', related_name='proctor_solo_feedback_rating', default=None, null=True, on_delete=models.CASCADE)
    is_trainee_implant = models.BooleanField(db_column='IsTraineeImplantWithOutProctor', default=False)
    any_leason = models.TextField(db_column='AnyLeasonThatYouWantToShare')
    report = models.FileField(upload_to='uploads/', db_column="ProctorReport", null=True, blank=True)
    class Meta:
        db_table = 'SoloSmartProctorFeedBack'


class ProctorshipCertificateForm(Base):
    certificate = models.FileField(db_column='Certificate', upload_to='uploads/', null=True,
                                       blank=True, default=None)

    proctorship = models.ForeignKey(Proctorship, db_column='ProctorshipID',
                                         related_name='certificate_form_proctorship', default=None,
                                         null=True, on_delete=models.CASCADE)

    class Meta:
        db_table = "ProctorshipCertificateForm"

