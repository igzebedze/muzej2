from django.contrib import admin
from evidenca import models

class VirAdmin(admin.ModelAdmin):
    list_display = ('sifra', 'podrocje', 'naslov', 'show_link')
    list_filter = ('podrocje', 'vrsta')
    search_fields = ('naslov', 'vsebina')
    date_hierarchy = 'datum'

class RacunalnikAdmin(admin.ModelAdmin):
    list_display = ('nakup', 'kraj', 'ime', 'nosilec', 'lastnistvo')
    list_filter = ('lastnistvo', 'kraj', 'proizvajalec')
    date_hierarchy = 'nakup'
    search_fields = ('opombe', 'tip', 'opis', 'opombe', 'proizvajalec')

class OrganizacijaAdmin(admin.ModelAdmin):
    list_display = ('ime', 'naslov', 'url')

admin.site.register(models.dosezek)
admin.site.register(models.organizacija, OrganizacijaAdmin)
admin.site.register(models.oseba)
admin.site.register(models.racunalnik, RacunalnikAdmin)
admin.site.register(models.sluzba)
admin.site.register(models.vir, VirAdmin)