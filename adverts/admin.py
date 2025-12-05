from django.contrib import admin
from .models import Advert, Type, Selection,Favourite

# Register your models here.
admin.site.register(Advert)
admin.site.register(Type)
admin.site.register(Selection)
admin.site.register(Favourite)
