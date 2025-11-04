from django.contrib import admin

# Register your models here.
from .models import UzWord, OT, SIFAT

admin.site.register(UzWord)
admin.site.register(OT)
admin.site.register(SIFAT)