from django.contrib import admin
from .models import Event, EventRSVP, EventType
# Register your models here.
admin.site.register(Event)
admin.site.register(EventRSVP)
admin.site.register(EventType)
