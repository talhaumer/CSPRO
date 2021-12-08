from django.contrib import admin

# Register your models here.
from api.status.models import Status, Proposal, ProctorshipProctors

#
admin.site.register(Status)
admin.site.register(Proposal)
admin.site.register(ProctorshipProctors)