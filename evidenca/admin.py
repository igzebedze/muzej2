from django.contrib import admin
from evidenca import models
from inventura import models as inventura
from django.utils.html import format_html
from django.contrib.admin import SimpleListFilter

class VirAdmin(admin.ModelAdmin):
    list_display = ('sifra', 'podrocje', 'naslov', 'sibek', 'show_link')
    list_filter = ('podrocje', 'vrsta', 'sibek')
    search_fields = ('naslov', 'vsebina')
    date_hierarchy = 'datum'
    list_editable = ('sibek',)

class RacunalnikAdmin(admin.ModelAdmin):
    list_display = ('nakup', 'kraj', 'ime', 'nosilec', 'lastnistvo')
    list_filter = ('generacija', 'lastnistvo', 'tip', 'uporaba', 'kraj')
    date_hierarchy = 'nakup'
    raw_id_fields = ('eksponat',)
    search_fields = ('opombe', 'tip', 'opis', 'proizvajalec__ime', 'nosilec__ime')
    filter_horizontal = ('organizacija','viri',)

class RacunalnikInline(admin.StackedInline):
    model = models.racunalnik
    filter_horizontal = ('organizacija','viri')

class OrganizacijaAdmin(admin.ModelAdmin):
    list_display = ('ime', 'naslov', 'racunalnikov', 'podrocje', 'latlong', 'url')
    #list_editable = ('ime', 'naslov', 'podrocje', 'latlong')
    list_display_links = ('ime',)
    filter_horizontal = ('partner',)
    search_fields = ('ime', 'naslov', 'povzetek', 'opis', 'podrocje')
    inlines = [
        RacunalnikInline,
    ]

    def racunalnikov(self, obj):
        return obj.nosilec.count() + obj.clan.count()

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

class SluzbaFilter(SimpleListFilter):
    title = 'sluzba_' # or use _('country') for translated title
    parameter_name = 'sluzba'

    def lookups(self, request, model_admin):
        organizations = set()
        for c in model_admin.model.objects.all():
            for cc in c.sluzba.all():
                organizations.add(cc)
        return [(c.pk, c.ime) for c in organizations]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(sluzba__id__exact=self.value())

class OsebaAdmin(admin.ModelAdmin):
    list_display = ('ime','rojen', 'get_jobs', 'pogovor', 'link')
    date_hierarchy = 'rojstvo'
    search_fields = ('ime', 'povzetek', 'opis')
    list_filter = ('spol',  SluzbaFilter)
    filter_horizontal = ('dosezek', 'sluzba')

    def link(self,obj):
        url = next((s for s in (obj.url, obj.wiki_sl, obj.wiki_en, obj.linkedin, obj.slobio) if s), '')
        if url:
            return format_html("<a href='{url}' target='_blank'>Vir</a>", url=url)
        else:
            return ''
    def rojen(self,obj):
        if obj.rojstvo:
            return obj.rojstvo.year
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

#class EksponatInline(admin.StackedInline):
 #   model = inventura.Eksponat.through
  #  filter_horizontal = ('organizacija','viri')

class ZbirateljAdmin(admin.ModelAdmin):
    list_display = ('oseba', 'kraj', 'eksponatov')
    list_filter = ('lokacija__kraj',)
    filter_horizontal = ('eksponat',)
#    inlines = [
 #       EksponatInline,
  #  ]

#class SluzbaAdmin(admin.ModelAdmin):
#    list_display = ('naziv', 'organizacija','od', 'do', 'naziv')
    #filter_horizontal = ('organizacija',)

admin.site.register(models.dosezek, DosezekAdmin)
admin.site.register(models.organizacija, OrganizacijaAdmin)
admin.site.register(models.oseba, OsebaAdmin)
admin.site.register(models.racunalnik, RacunalnikAdmin)
admin.site.register(models.pogovor, PogovorAdmin)
admin.site.register(models.vir, VirAdmin)
admin.site.register(models.zbiratelj, ZbirateljAdmin)

#admin.site.register(models.sluzba, SluzbaAdmin)
