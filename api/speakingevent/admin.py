from django.contrib import admin

from api.speakingevent.models import Event, EventStatus, Speaker, SpeakingEvent

# Register your models here.
admin.site.register(Event)
admin.site.register(SpeakingEvent)
admin.site.register(Speaker)
admin.site.register(EventStatus)
