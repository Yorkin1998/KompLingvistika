from django.contrib import admin

# Register your models here.
from .models import UzWord, OT, SIFAT, UmumiyTurkum

admin.site.register(UzWord)

@admin.register(UmumiyTurkum)
class UmumiyTurkumadmin(admin.ModelAdmin):
    list_display = ['id','word','type_is']
    search_fields = ['word']
    list_filter = ['type_is',]
