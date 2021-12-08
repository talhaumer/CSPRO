from django.contrib import admin

# Register your models here.
from api.invoice.models import Invoice, AttendanceForm

admin.site.register(Invoice)
admin.site.register(AttendanceForm)