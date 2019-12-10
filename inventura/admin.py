from django.contrib import admin
from django.contrib.auth.models import User

from simple_history.admin import SimpleHistoryAdmin
#from import_export import resources
import wikipedia

from inventura import models

#class EksponatResource(resources.ModelResource):
#    class Meta:
#        model = Eksponat

	
class PregledAdmin(SimpleHistoryAdmin):
	list_display = ('primerek', 'izvajalec', 'datum', 'deluje')
	list_filter = ('izvajalec', 'deluje')
	date_hierarchy = 'datum'
	
class PrimerekInline(admin.TabularInline):
	model = models.Primerek
	fields = ('eksponat', 'serijska_st', 'leto_proizvodnje', 'inventariziral')
	readonly_fields = ('eksponat', 'serijska_st', 'leto_proizvodnje', 'inventariziral')	
	extra = 0

class PregledInline(admin.TabularInline):
	model = models.Pregled
	extra = 0
	
class EksponatAdmin(SimpleHistoryAdmin):
	list_select_related = True
	inlines = [
			PrimerekInline,
	]
	list_display = ('ime', 'kategorija', 'proizvajalec', 'leto_proizvodnje', 'st_primerkov')
	list_filter = ('kategorija', 'proizvajalec')
	search_fields = ('ime', 'tip')
	date_hierarchy = ('created_at')
	ordering = ('-updated_at',)
	
#	def get_form(self, request, obj=None, **kwargs):
#		form = super(EksponatAdmin, self).get_form(request, obj, **kwargs)
#		if obj and obj.ime and not obj.wikipedia:
#			wiki = wikipedia.page(wikipedia.search(obj.ime, results=1))
#			if wiki:
#				form.base_fields['onlinephoto'].initial = wiki.images[0]
#				form.base_fields['wikipedia'].initial = wiki.url
#				obj.wikipedia = wiki.url
#				obj.onlinephoto = wiki.images[0]
#		return form
	
class OsebaAdmin(admin.ModelAdmin):
	search_fields = ('ime',)

class ProizvajalecAdmin(admin.ModelAdmin):
	list_filter = ('drzava',)

class RazstaveAdmin(admin.TabularInline):
	model = models.Primerek.razstava_set.through

class PrimerekAdmin(SimpleHistoryAdmin):
	filter_horizontal = ('povezani',)
	list_display = ('stevilka', 'eksponat', 'serijska_st', 'leto_proizvodnje', 'st_razstav')
	list_filter = ('lokacija', 'eksponat__kategorija')
	readonly_fields = ('inventariziral', 'datum_inventarizacije')
	search_fields = ('inventarna_st', 'serijska_st', 'eksponat__ime')
	inlines = [ RazstaveAdmin, PregledInline ]
	autocomplete_fields = ['eksponat']

	def save_model(self, request, obj, form, change):
		if not change:
			obj.inventariziral = request.user
		obj.save()

class VhodAdmin(SimpleHistoryAdmin):
	list_display = ('stevilka', 'lastnik', 'razlog', 'prevzel', 'cas_prevzema', 'inventorizirano')
	inlines = [
			PrimerekInline,
	]
	search_fields = ('opis',)
	fieldsets = (
			(None, {
				'fields': (	'izrocitelj', 'lastnik', 'opis', 'razlog',
						'zacasna_lokacija', 'prevzel', 'cas_prevzema'),
			}),
			('Vrnitev', {
				'fields': (	'dogovorjeni_datum_vrnitve', 'datum_vrnitve', 'opombe'),
			}),
		)

class RazstavaAdmin(SimpleHistoryAdmin):
	filter_horizontal = ('primerki','avtorji')
	list_display = ('naslov', 'otvoritev', 'lokacija')
	search_fields = ('naslov', 'lokacija', 'opis', 'naslov', 'avtorji',)
	list_filter = ('lokacija',)
	
class IzhodAdmin(SimpleHistoryAdmin):
	filter_horizontal = ('primerki',)
	list_display = ('prevzemnik', 'ustanova', 'namen')
	list_filter = ('namen', 'ustanova')


class LokacijaAdmin(admin.ModelAdmin):
	list_display = ('ime', 'naslov', 'st_primerkov')
	
admin.site.register(models.Kategorija)
admin.site.register(models.Proizvajalec, ProizvajalecAdmin)
admin.site.register(models.Eksponat, EksponatAdmin)
admin.site.register(models.Oseba, OsebaAdmin)
admin.site.register(models.Vhod, VhodAdmin)
admin.site.register(models.Lokacija, LokacijaAdmin)
admin.site.register(models.Primerek, PrimerekAdmin)
admin.site.register(models.Razstava, RazstavaAdmin)
admin.site.register(models.Izhod, IzhodAdmin)
admin.site.register(models.Pregled, PregledAdmin)
