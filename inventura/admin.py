from django.contrib import admin
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from simple_history.admin import SimpleHistoryAdmin
#from import_export import resources
#import wikipedia

from inventura import models

#class EksponatResource(resources.ModelResource):
#	class Meta:
#		model = Eksponat

class VhodiCountListFilter(admin.SimpleListFilter):
	# Human-readable title which will be displayed in the
	# right admin sidebar just above the filter options.
	title = 'Provenienca'

	# Parameter for the filter that will be used in the URL query.
	parameter_name = 'ima_vhod'

	def lookups(self, request, model_admin):
		"""
		Returns a list of tuples. The first element in each
		tuple is the coded value for the option that will
		appear in the URL query. The second element is the
		human-readable name for the option that will appear
		in the right sidebar.
		"""
		return [('yes', "Ima vhod"), ('no', "Nima vhoda")]

	def queryset(self, request, queryset):
		"""
		Returns the filtered queryset based on the value
		provided in the query string and retrievable via
		`self.value()`.
		"""

		if self.value() == 'yes':
			return queryset.exclude(vhodni_dokument__isnull=self.value())
		elif self.value() == 'no':
			return queryset.filter(vhodni_dokument__isnull=self.value())
		else:
			return queryset


def batch_update_view(model_admin, request, queryset, field_name):

		# removes all other fields from the django admin form for a model
	def remove_fields(form):
		for field in list(form.base_fields.keys()):
			if not field == field_name:
				del form.base_fields[field]
		return form

		# the return value is the form class, not the form class instance
	form_class = remove_fields(model_admin.get_form(request))

	if request.method == 'POST':
		form = form_class()

		# the view is already called via POST from the django admin changelist
		# here we have to distinguish between just showing the intermediary view via post
		# and actually confirming the bulk edits
		# for this there is a hidden field 'form-post' in the html template
		if 'form-post' in request.POST:
			form = form_class(request.POST)
			if form.is_valid():
				for item in queryset.all():
					setattr(item, field_name, form.cleaned_data[field_name])
					item.save()
				model_admin.message_user(request, "Changed {} on {} items".format(field_name, queryset.count()))
				return redirect(request.get_full_path())

	return render(
			request,
			'admin/batch_editing_intermediary.html',
			context={
				'form': form,
				'items': queryset,
				'media': model_admin.media,
			}
		)
	
class PregledAdmin(SimpleHistoryAdmin):
	list_display = ('primerek', 'izvajalec', 'datum', 'deluje')
	list_filter = ('izvajalec', 'deluje')
	date_hierarchy = 'datum'
	search_fields = ('primerek','zapiski',)
	
class PrimerekInline(admin.TabularInline):
	model = models.Primerek
	fields = ('inventarna_st', 'eksponat', 'serijska_st', 'leto_proizvodnje', 'inventariziral')
	readonly_fields = ('inventarna_st', 'eksponat', 'serijska_st', 'leto_proizvodnje', 'inventariziral')	
	extra = 0

class PregledInline(admin.TabularInline):
	model = models.Pregled
	extra = 0
	
class EksponatAdmin(SimpleHistoryAdmin):
	list_select_related = True
	list_editable = ('ime', 'tip', 'kategorija',)
	#inlines = [ PrimerekInline, ]
	list_display = ('proizvajalec', 'ime', 'tip', 'kategorija',  'leto_proizvodnje', 'st_primerkov')
	list_filter = ('kategorija', 'proizvajalec')
	search_fields = ('ime', 'tip')
	date_hierarchy = 'created_at'
	ordering = ('-updated_at',)
	actions = ['spremeni_kategorijo']
	
	def spremeni_kategorijo(self, request, queryset):
		return batch_update_view(
			model_admin=self,
			request=request,
			queryset=queryset,
			# this is the name of the field on the YourModel model
			field_name='kategorija',
		)
	spremeni_kategorijo.short_description = "Spremeni kategorijo izbranim eksponatom"
		
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
	search_fields = ('ime',)
	list_display = ("ime", "drzava", "st_eksponatov")

class RazstaveAdmin(admin.TabularInline):
	model = models.Primerek.razstava_set.through

class PrimerekAdmin(SimpleHistoryAdmin):
	list_select_related = True
	#filter_horizontal = ('povezani',)
	raw_id_fields = ("povezani",)
	list_display = ('stevilka', 'eksponat', 'serijska_st', 'leto_proizvodnje', 'st_razstav', 'ima_vhod')
	list_filter = ('lokacija', VhodiCountListFilter, 'eksponat__kategorija')
	readonly_fields = ('inventariziral', 'datum_inventarizacije')
	search_fields = ('inventarna_st', 'serijska_st', 'eksponat__ime', 'eksponat__proizvajalec__ime', 'zgodovina', 'stanje')
	inlines = [ RazstaveAdmin, PregledInline ]
	date_hierarchy = 'datum_inventarizacije'
	#date_hierarchy = 'leto_proizvodnje'
	autocomplete_fields = ['eksponat']	
	actions = ['spremeni_eksponat', 'premakni_polico', 'naredi_vhod']

	def save_model(self, request, obj, form, change):
		if not change:
			obj.inventariziral = request.user
		obj.save()
	
	def spremeni_eksponat(self, request, queryset):
		return batch_update_view(
			model_admin=self,
			request=request,
			queryset=queryset,
			# this is the name of the field on the YourModel model
			field_name='eksponat',
		)
	spremeni_eksponat.short_description = "Spremeni eksponat izbranim primerkom"
	def premakni_polico(self, request, queryset):
		return batch_update_view(
			model_admin=self,
			request=request,
			queryset=queryset,
			# this is the name of the field on the YourModel model
			field_name='polica',
		)
	premakni_polico.short_description = "Nastavi polico izbranim primerkom"
	def naredi_vhod(self, request, queryset):
		return batch_update_view(
			model_admin=self,
			request=request,
			queryset=queryset,
			# this is the name of the field on the YourModel model
			field_name='vhodni_dokument',
		)
	naredi_vhod.short_description = "Nastavi vhodni dokument"
		
class VhodAdmin(SimpleHistoryAdmin):
	list_display = ('stevilka', 'lastnik', 'razlog',  'prevzel', 'cas_prevzema', 'inventorizirano')
	inlines = [ PrimerekInline,]
	search_fields = ('opis',)
	fieldsets = (
			('Sprejem', {
				'fields': (	'izrocitelj', 'lastnik', 'opis', 'razlog','dovoli_objavo',
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
	date_hierarchy = 'otvoritev'
	
class IzhodAdmin(SimpleHistoryAdmin):
	filter_horizontal = ('primerki',)
	list_display = ('prevzemnik', 'ustanova', 'namen')
	list_filter = ('namen', 'ustanova')


class LokacijaAdmin(admin.ModelAdmin):
	list_display = ('ime', 'naslov', 'st_primerkov')

class KveriAdmin(admin.ModelAdmin):
	list_display = ('kveri', 'created_at')
	date_hiearchy = 'created_at'
	
class ProjektAdmin(admin.ModelAdmin):
	list_filter = ('vrsta', 'status', 'potrebe', 'nosilec')
	date_hiearchy = 'datum'
	search_fields = ('opis', 'rezultat')
	list_display = ('naslov', 'nosilec', 'status', 'potrebe', 'vrsta', 'datum')
	
class TiskovinaAdmin(admin.ModelAdmin):
	search_fields = ('besedilo', 'kazalo')	
	date_hiearchy = 'datum'
	
admin.site.register(models.Kategorija)
admin.site.register(models.Iskalnik)
admin.site.register(models.Proizvajalec, ProizvajalecAdmin)
admin.site.register(models.Eksponat, EksponatAdmin)
admin.site.register(models.Oseba, OsebaAdmin)
admin.site.register(models.Vhod, VhodAdmin)
admin.site.register(models.Lokacija, LokacijaAdmin)
admin.site.register(models.Primerek, PrimerekAdmin)
admin.site.register(models.Razstava, RazstavaAdmin)
admin.site.register(models.Izhod, IzhodAdmin)
admin.site.register(models.Pregled, PregledAdmin)
admin.site.register(models.Kveri, KveriAdmin)
admin.site.register(models.Tiskovina)
admin.site.register(models.Projekt, ProjektAdmin)
