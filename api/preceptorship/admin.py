from django.contrib import admin

# Register your models here.
from api.preceptorship.models import Preceptorship, TraineePreceptorshipProfile, PreceptorshipTraineeUploads, \
    AttendanceFormPerceptorship, InvoicePerceptorship, PreceptorshipStatus

admin.site.register(Preceptorship)
admin.site.register(TraineePreceptorshipProfile)
admin.site.register(PreceptorshipTraineeUploads)
admin.site.register(AttendanceFormPerceptorship)
admin.site.register(InvoicePerceptorship)
admin.site.register(PreceptorshipStatus)
