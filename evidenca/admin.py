from django.contrib import admin
from evidenca import models
from django.utils.html import format_html

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
    list_display = ('pk', 'ime', 'naslov', 'podrocje', 'latlong', 'url')
    #list_editable = ('ime', 'naslov', 'podrocje', 'latlong')
    list_display_links = ('pk',)

class PogovorAdmin(admin.ModelAdmin):
    list_display = ('oseba', 'datum', 'avtor', 'za_objavo', 'zvok', 'slika', 'text')
    date_hierarchy = 'datum'
    list_filter = ('za_objavo','avtor')

    def zvok(self,obj):
        return bool(obj.audio)
    def slika(self,obj):
        return bool(obj.video)
    def text(self,obj):
        return bool(obj.prepis)
    zvok.boolean=True
    slika.boolean=True
    text.boolean=True

class OsebaAdmin(admin.ModelAdmin):
    list_display = ('ime','rojstvo', 'pogovor', 'link')
    date_hierarchy = 'rojstvo'
    search_fields = ('ime', 'povzetek', 'opis')
    list_filter = ('spol', 'sluzba', )

    def link(self,obj):
        url = next((s for s in (obj.url, obj.wiki_sl, obj.wiki_en, obj.linkedin, obj.slobio) if s), '')
        if url:
            return format_html("<a href='{url}' target='_blank'>Vir</a>", url=url)
        else:
            return ''
    def pogovor(self,obj):
        return bool(obj.pogovor_set.count())
    pogovor.boolean=True

class DosezekAdmin(admin.ModelAdmin):
    list_display = ('ime', 'vrsta', 'pomen', 'od', 'do')
    date_hierarchy = 'od'
    search_fields = ('ime', 'opis', 'povzetek')
    list_filter = ('vrsta', 'pomen', )
    filter_horizontal = ('eksponat',)

class SluzbaAdmin(admin.ModelAdmin):
    list_display = ('naziv',)
    filter_horizontal = ('organizacija',)

admin.site.register(models.dosezek, DosezekAdmin)
admin.site.register(models.organizacija, OrganizacijaAdmin)
admin.site.register(models.oseba, OsebaAdmin)
admin.site.register(models.racunalnik, RacunalnikAdmin)
admin.site.register(models.sluzba, SluzbaAdmin)
admin.site.register(models.pogovor, PogovorAdmin)
admin.site.register(models.vir, VirAdmin)