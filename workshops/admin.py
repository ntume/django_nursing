from django.contrib import admin
from .models import Workshop, WorkshopRSVP, WorkshopType
# Register your models here.
admin.site.register(Workshop)
admin.site.register(WorkshopRSVP)
admin.site.register(WorkshopType)
