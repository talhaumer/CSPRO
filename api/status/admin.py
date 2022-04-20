from django.contrib import admin

# Register your models here.
from api.status.models import ProctorshipProctors, Proposal, Status

#
admin.site.register(Status)
admin.site.register(Proposal)
admin.site.register(ProctorshipProctors)
