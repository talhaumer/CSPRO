from django.contrib import admin

from api.proctorship.models import ConstantData, Proctorship

# Register your models here.
admin.site.register(Proctorship)
admin.site.register(ConstantData)
