from django.contrib import admin
from django.contrib.auth.models import User
from simple_history.admin import SimpleHistoryAdmin

from inventura import models

class PrimerekInline(admin.StackedInline):
	model = models.Primerek
	extra = 0

class EksponatAdmin(SimpleHistoryAdmin):
	inlines = [
			PrimerekInline,
	]
	list_display = ('ime', 'tip', 'proizvajalec', 'leto_proizvodnje', 'st_primerkov')
	list_filter = ('kategorija', 'proizvajalec')
	search_fields = ('ime', 'tip')

class OsebaAdmin(admin.ModelAdmin):
	search_fields = ('ime',)

class ProizvajalecAdmin(admin.ModelAdmin):
	list_filter = ('drzava',)

class RazstaveAdmin(admin.StackedInline):
	model = models.Primerek.razstava_set.through

class PrimerekAdmin(SimpleHistoryAdmin):
	list_display = ('stevilka', 'eksponat', 'serijska_st', 'leto_proizvodnje')
	list_filter = ('lokacija',)
	readonly_fields = ('inventariziral', 'datum_inventarizacije')
	search_fields = ('inventarna_st', 'serijska_st', 'eksponat__ime')
	inlines = [ RazstaveAdmin ]

	def save_model(self, request, obj, form, change):
		if not change:
			obj.inventariziral = request.user
		obj.save()

class VhodAdmin(SimpleHistoryAdmin):
	list_display = ('stevilka', 'lastnik', 'razlog', 'prevzel', 'cas_prevzema', 'inventorizirano')

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

admin.site.register(models.Kategorija)
admin.site.register(models.Proizvajalec, ProizvajalecAdmin)
admin.site.register(models.Eksponat, EksponatAdmin)
admin.site.register(models.Oseba, OsebaAdmin)
admin.site.register(models.Vhod, VhodAdmin)
admin.site.register(models.Lokacija)
admin.site.register(models.Primerek, PrimerekAdmin)
admin.site.register(models.Razstava, SimpleHistoryAdmin)
admin.site.register(models.Izhod, SimpleHistoryAdmin)
