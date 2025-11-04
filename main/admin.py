from django.contrib import admin

# Register your models here.
from .models import UzWord, OT, SIFAT

admin.site.register(UzWord)

@admin.register(OT)
class OTadmin(admin.ModelAdmin):
    list_display = ['id','word',]
    search_fields = ['word']

@admin.register(SIFAT)
class SIFATadmin(admin.ModelAdmin):
    list_display = ['id','word',]
    search_fields = ['word']