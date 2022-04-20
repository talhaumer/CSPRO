from django.contrib import admin

# Register your models here.
from api.preceptorship.models import (
    AttendanceFormPerceptorship,
    InvoicePerceptorship,
    Preceptorship,
    PreceptorshipStatus,
    PreceptorshipTraineeUploads,
    TraineePreceptorshipProfile,
)

admin.site.register(Preceptorship)
admin.site.register(TraineePreceptorshipProfile)
admin.site.register(PreceptorshipTraineeUploads)
admin.site.register(AttendanceFormPerceptorship)
admin.site.register(InvoicePerceptorship)
admin.site.register(PreceptorshipStatus)
