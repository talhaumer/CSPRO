from django.contrib import admin
from api.models import Products, Hospital, Hcp_role, Languages, Solution, Audience, Region, EventType, \
    HospitalCountires, Approach, AreaOfExperties

# Register your models here.
admin.site.register(Products)
admin.site.register(Hospital)
# admin.site.register(Hcp_role)
# admin.site.register(Languages)
# admin.site.register( Solution)
# admin.site.register(Audience)
# admin.site.register(Region)
admin.site.register(EventType)
admin.site.register(HospitalCountires)
# admin.site.register(Approach)
# admin.site.register(AreaOfExperties)
