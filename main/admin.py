from django.contrib import admin

# Register your models here.
from .models import UzWord, OT, Patterns, UmumiyTurkum

admin.site.register(UzWord)

@admin.register(UmumiyTurkum)
class UmumiyTurkumadmin(admin.ModelAdmin):
    list_display = ['id','word','type_is']
    search_fields = ['word']
    list_filter = ['type_is',]

@admin.register(Patterns)
class PatternsAdmin(admin.ModelAdmin):
    # Ko‘rinadigan ustunlar
    list_display = ('word', 'type_of_these')
    
    # Filter qo‘shish
    list_filter = ('type_of_these',)
    
    # Qidiruv uchun
    search_fields = ('word',)
    
    # Formdagi joylashtirish (ixtiyoriy)
    fieldsets = (
        (None, {
            'fields': ('word', 'type_of_these')
        }),
    )
