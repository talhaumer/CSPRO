from django.contrib import admin

# Register your models here.
from api.feedback.models import SoloSmartProctorFeedBack, MemoProctorFeedBack, TraineeFeedback, \
    ProctorshipProctorFeedback, Reason

admin.site.register(SoloSmartProctorFeedBack)
#
admin.site.register( MemoProctorFeedBack)
#
admin.site.register(TraineeFeedback)
#
admin.site.register(ProctorshipProctorFeedback)
admin.site.register(Reason)