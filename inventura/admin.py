from django.contrib import admin
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from simple_history.admin import SimpleHistoryAdmin
#from import_export import resources
import wikipedia

from inventura import models

#class EksponatResource(resources.ModelResource):
#	class Meta:
#		model = Eksponat

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
				model_admin.message_user(request, "Changed category on {} items".format(queryset.count()))
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
	#inlines = [ PrimerekInline, ]
	list_display = ('ime', 'kategorija', 'proizvajalec', 'leto_proizvodnje', 'st_primerkov')
	list_filter = ('kategorija', 'proizvajalec')
	search_fields = ('ime', 'tip')
	date_hierarchy = ('created_at')
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
		batch_update_offer.short_description = "spremeni kategorijo izbranim eksponatom"
	
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
