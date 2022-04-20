from django.contrib import admin

# Register your models here.
from api.masterproctorship.models import (
    MasterProctorship,
    MasterProctorshipFeedback,
    MasterProctorshipStatus,
)

admin.site.register(MasterProctorship)
admin.site.register(MasterProctorshipFeedback)
admin.site.register(MasterProctorshipStatus)
