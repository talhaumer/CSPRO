from django.contrib import admin
from api.proctors.models import Proctors, ProctorsHospital

# Register your models here.

admin.site.register(Proctors)
admin.site.register(ProctorsHospital)