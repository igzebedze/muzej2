import re
#import wikipedia
#import wptools
#import wikitextparser as wtp
#import urllib.parse
import random
import os.path
import pprint

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.sites.shortcuts import get_current_site
from django.http import Http404
from django import forms
from django.views.generic import ListView, DetailView
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.db.models import Q

from .serializers import PrimerekSerializer, RazstavaSerializer, KategorijaSerializer
from rest_framework import viewsets, generics
from inventura.models import Vhod, Primerek, Lokacija, Izhod, Eksponat, Kategorija, Razstava, Proizvajalec, Kveri, Tiskovina, Stran


class KategorijeViewSet(viewsets.ReadOnlyModelViewSet):
	queryset = Kategorija.objects.all()
	serializer_class = KategorijaSerializer
	pagination_class = None
		
class RazstaveViewSet(viewsets.ReadOnlyModelViewSet):
	queryset = Razstava.objects.all()
	serializer_class = RazstavaSerializer
	def get_queryset(self):
		queryset = Razstava.objects.all()
		id = self.kwargs.get('pk', None)
		if id is not None:
			queryset = queryset.filter(pk=id)
		return queryset

class HeroViewSet(viewsets.ReadOnlyModelViewSet):
	queryset = Primerek.objects.all()
	serializer_class = PrimerekSerializer

	def get_queryset(self):
		queryset = Primerek.objects.filter(eksponat__isnull=False)
		id = self.kwargs.get('pk', None)
		if id is not None:
			queryset = queryset.filter(inventarna_st=id)

		kveri = self.request.query_params.get('kveri', None)
		if kveri is not None:
			kv = ''
			for k in kveri.split():
				kv = kv + "+" + k + " "
				queryset = queryset.filter(iskalnik__vsebina__icontains=k)
			#queryset = queryset.filter(iskalnik__vsebina__search=kveri)			
			k = Kveri(kveri=kveri)
			k.save()
			print (kveri)

		return queryset

@login_required
def update_infobox(request, pk=None):
	e = Eksponat.objects.get(id=pk)
	
	# if this is a POST request we need to process the form data
	# if request.method == 'POST':
	# 	if 'wikiurl' in request.POST:
	# 		wikiurl = urllib.parse.unquote(request.POST.get('wikiurl'))
	# 		e.wikipedia = wikiurl
	# 	if 'wikiimage' in request.POST:
	# 		wikiimage = urllib.parse.unquote(request.POST.get('wikiimage'))
	# 		e.onlinephoto = wikiimage
	# 	if 'infobox' in request.POST:
	# 		infobox = urllib.parse.unquote(request.POST.get('infobox'))
	# 		e.infobox = infobox
	# 	e.save()
			
	return redirect('/eksponat/%d/' % (pk))

def root(request):
	return redirect('/admin/')

class PrimerekList(ListView):
	model = Primerek

class ListkiForm(forms.Form):
	stevilke = forms.CharField(widget=forms.Textarea)
	
@login_required
def listki(request):
	if request.method == 'POST':
		form = ListkiForm(request.POST)
		if form.is_valid():
			stevilke = form.cleaned_data['stevilke']

			id_set = stevilke.splitlines()
			primerki = []
			for id in id_set:
				try:
					primerek = Primerek.objects.get(pk=int(id))
					primerki.append(primerek)
				except Primerek.DoesNotExist:
					messages.add_message(request, messages.ERROR,
							"Ne najdem primerka %d!" % (int(id),))

			#print (primerki)
			context = { 'object_list': primerki }
			return render(request, 'listki.html', context)
	
	else:
		form = ListkiForm() # An unbound form
		
	context = {'form': form}
	return render(request, 'listkiform.html', context)	

def revijaYearsView(request, tip):
	object_list = Tiskovina.objects.filter(eksponat__tip=tip)
	context = {}
	site = request.META['HTTP_HOST']
	if site == 'revije.muzej.si':
		context['root'] = ''
	else:
		context['root'] = '/revije'
	context['domain'] = site
	context['object_list'] = object_list
	context['selected'] = tip
	context['eksponat'] = Eksponat.objects.get(tip=tip)
	return render(request, "inventura/letniki.html", context)

class revijeYearsView(ListView):
	model = Tiskovina
	ordering = ['eksponat']
	template_name = "inventura/letniki.html"

	def get_context_data(self, **kwargs):
		context = super(revijeYearsView, self).get_context_data(**kwargs)
		q = self.request.GET.get("q")
		context['query'] = q
		site = self.request.META['HTTP_HOST']
		if site == 'revije.muzej.si':
			context['root'] = ''
		else:
			context['root'] = '/revije'
		context['domain'] = site
		return context

# todo add snippets and page numbers
	def get_queryset(self):
		q = self.request.GET.get("q")
		object_list = self.model.objects.order_by('eksponat')
		if q:
			from haystack.query import SearchQuerySet
			results = SearchQuerySet().filter(content=q).models(Stran)
			revije = []
			for o in results:
				revije.append(o.object.tiskovina)
			if len(revije) > 0:
				object_list=revije
		return object_list

class revijaView(DetailView):
	model = Tiskovina

def revijaJSView(request, pk):
	e = Tiskovina.objects.get(pk=pk)
	pdf = e.pdf
	location = pdf[0:-4]
	naslovnica = e.naslovnica.split('/')[-1]
	start = int(naslovnica.split('.')[0])
	context = {
		'object': e,
		'location': location,
		'pages': e.pages, # todo: get this from database
		'start': start, # todo: get this from datamase
		'range': range(start, start + e.pages)
	}
	return render(request, 'inventura/revija.js', context, content_type='text/javascript')

def revijaThumbsView(request, pk):
	e = Tiskovina.objects.get(pk=pk)
	pdf = e.pdf
	location = pdf[0:-4]
	naslovnica = e.naslovnica.split('/')[-1]
	start = int(naslovnica.split('.')[0])
	context = {
		'object': e,
		'location': location,
		'pages': e.pages, # todo: get this from database
		'start': start, # todo: get this from datamase
		'range': range(start, start + e.pages)
	}
	return render(request, 'inventura/thumbs.js', context, content_type='text/javascript')

class KategorijaList(ListView):
	model = Kategorija

class GalerijaList(ListView):
	model = Kategorija
	template_name = "inventura/galerija.html"
	
class ProizvajalecList(ListView):
	model = Proizvajalec

# todo: grab and render wikipedia infobox if link avaialable, else offer to add wiki
class EksponatView(DetailView):
	model = Eksponat

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		e = self.get_object()

# list of exhibitions
		razstave = []
		for p in e.primerek_set.all():
			for r in p.razstava_set.all():
				if r not in razstave:
					razstave.append(r) 
		context['razstave'] = razstave

# list of donors
		donatorji = []
		for p in e.primerek_set.all():
			if p.donator and p.donator not in donatorji:
				donatorji.append(p.donator) 
		context['donatorji'] = donatorji

# navigation
		context['next'] = e.id + 1
		context['prev'] = e.id - 1

# if we stored infobox before, we assume there is nothing else to do
#		if e.infobox:
#			return context

# 		w = e.wikipedia
# # if we don't have wiki page yet, search api for the object
# 		if self.request.user.is_authenticated and (not e.wikipedia or not e.onlinephoto):
# 			search = e.ime # e.proizvajalec.ime + " " + 
# 			#if e.tip:
# 			#	search = search + " " + e.tip
# 			search = search.replace("tipkovnica", "keyboard")
# 			search = search.replace("usmerjevalnik", "router")
# 			search = search.replace("kasetar", "casette player")
# 			search = search.replace("miška", "mouse")
# 			search = search.replace("ZDA", "USA")
# 			print ('checking: ' + search)
# 			try:
# 				pages = wikipedia.search(search, results=5)
# 				print (pages)
# 				#wiki = wikipedia.page(wikipedia.search(search, results=1))
# 			except:
# 				print ('blah: ' + search)
# 			else:
# 				context['wiki'] = []
# 				for p in pages:
# 					try:
# 						page = wikipedia.page(p)
# 						#pp = pprint.PrettyPrinter(indent=4)
# 						#pp.pprint (page)
# 					except:
# 						pass
# 					else:
# 						wiki = {'save': False}
# 						save = False
# 						if not e.wikipedia:
# 							wiki['wikiurl'] = page.url
# 							#pp.pprint (page.url)
# 							wiki['wikiname'] = page.title
# 							save = True
# 						try:
# 							if not e.onlinephoto:
# 								wiki['wikiimage'] = page.images[0]
# 								wiki['wikiimages'] = page.images[0,5]
# 								save = True
# 						except:
# 							pass
						
# 						if save:
# 							context['wiki'].append(wiki)
# 							#print (wiki)

# # parse the data and store it
# 		if w and not e.infobox:
# 			slug = w.rsplit('/', 1)[-1]		# we only accept well formed wiki urls
# 			wiki = wptools.page(slug)
# 			try:
# 				page = wiki.get_restbase('/page/html/').data['html']
# 			except:
# 				pass
# 			else:
# 				infobox = re.findall("<table class=\"infobox.*?<\/table>", page)
# 				if infobox:
# 					context['infobox'] = "\n<br>\n".join(infobox)
		
		return context

class RazstavaView(DetailView):
	model = Razstava
	
def terminalView(request):
	context = {}
	return render(request, 'terminal.html', context)

def appView(request, category = '', object = ''):
	object_list = Eksponat.objects.order_by('ime')
	if object:
		object = Eksponat.objects.get(pk=object)
	if category and category == 'proizvajalec':
		object_list = Proizvajalec.objects.order_by('ime')
	elif category:
		category = Kategorija.objects.get(ime=category)
		object_list = category.eksponat_set.order_by('ime')
	else:
		object_list = Kategorija.objects.all
	context = {
		'object_list': object_list,
		'object': object,
		'category': category,
		'categories': Kategorija.objects.all,
#		'photos': queryset of random 100 eksponati with photos
	}
	return render(request, 'inventura/appview.html', context)

def appEksponat(request, pk):
	return render(request, 'inventura/appeksponat.html', {
        'object': Eksponat.objects.get(pk=pk),
    }, content_type='text/html')

def appProizvajalec(request, pk):
	p = Proizvajalec.objects.get(pk=pk)
	return render(request, 'inventura/appproizvajalec.html', {
        'object': p,
		'object_list': p.eksponat_set.order_by('kategorija'),
    }, content_type='text/html')

def HomeView(request):
	eksponati = Eksponat.objects.all()
	max_id = Eksponat.objects.order_by('-id')[0].id
	random_id = random.randint(1, max_id + 1)
	random_object = Eksponat.objects.filter(id=random_id)[0]
	context = {
		'razstave': Razstava.objects.order_by('-otvoritev'),
		'novosti': Primerek.objects.filter(eksponat__isnull=False).order_by('-datum_inventarizacije')[0:10],
		'eksponat': random_object,
	}
	return render(request, 'home.html', context)

# todo:
	# imajo vhod vs. ne
	# drzave pie chart
	# primerki po kategorijah
	# ?
def stat(request):
	drzave = {}
	kategorije = []
	leta = ['2023', '2022', '2021', '2020', '2019', '2012', '2011']
	primerki_leta = []
	
	for p in Proizvajalec.objects.all():
		drzave[p.drzava] = 1
	
	for e in Eksponat.objects.all():
		if e.proizvajalec:
			drzave[e.proizvajalec.drzava] = drzave[e.proizvajalec.drzava] + 1

	for leto in leta:
		for k in Kategorija.objects.all():
			p = Primerek.objects.filter(eksponat__kategorija=k, datum_inventarizacije__year=leto).count()
			k = {'leto': leto, 'kategorija': k.ime, 'primerkov': p}
			kategorije.append(k)		
	
	context = {
			'primerki_vhod_ja': Primerek.objects.exclude(eksponat__isnull=True).filter(vhodni_dokument__isnull=False).count(),
			'primerki_vhod_ne': Primerek.objects.exclude(eksponat__isnull=True).filter(vhodni_dokument__isnull=True).count(),
			'eksponati_kategorije': Kategorija.objects.all(),
			'eksponati_drzave': drzave,
			'primerki_leta': kategorije,
			'leta': leta
		}
	return render(request, 'stat.html', context)

@login_required
def izhod(request, id):
	izhod = Izhod.objects.get(pk=id)
	context = {
			'izhod': izhod,
		}
	return render(request, 'izhod.html', context)

@login_required
def izhod_short(request, id):
	try:
		izhod = Izhod.objects.get(pk=id)
	except Vhod.DoesNotExist:
		raise Http404
	return redirect(izhod)
	
@login_required
def vhod(request, id):
	vhod = Vhod.objects.get(pk=id)
	context = {
			'vhod': vhod,
		}
	return render(request, 'vhod.html', context)

@login_required
def vhod_short(request, id):
	try:
		vhod = Vhod.objects.get(pk=id)
	except Vhod.DoesNotExist:
		raise Http404
	return redirect(vhod)

@login_required
def primerek_short(request, id):
	try:
		primerek = Primerek.objects.get(pk=id)
	except Primerek.DoesNotExist:
		raise Http404
	return redirect(primerek)

class PremikForm(forms.Form):
	zapisnik = forms.CharField(widget=forms.Textarea)
	lokacija = forms.ModelChoiceField(queryset=Lokacija.objects.all())
	polica = forms.CharField()

@login_required
def premik(request):
	if request.method == 'POST':
		form = PremikForm(request.POST)
		if form.is_valid():
			zapisnik = form.cleaned_data['zapisnik']
			lokacija = form.cleaned_data['lokacija']
			polica = form.cleaned_data['polica']

			id_set = set()
			for id in re.findall("http://racunalniski-muzej.si/i/([0-9]+)/?", zapisnik, re.I):
				id_set.add(int(id))
			for id in re.findall("^([0-9]+)$", zapisnik, re.I):
				id_set.add(int(id))

			primerki = []
			for id in id_set:
				try:
					primerek = Primerek.objects.get(pk=id)
					primerki.append(primerek)
				except Primerek.DoesNotExist:
					messages.add_message(request, messages.ERROR,
							"Ne najdem primerka %d!" % (id,))

			for primerek in primerki:
				primerek.lokacija = lokacija
				primerek.polica = polica
				primerek.save()

			messages.add_message(request, messages.SUCCESS,
					"Premaknil %d primerkov na lokacijo %s, polica %s." % (len(primerki), lokacija, polica))

	else:
		form = PremikForm() # An unbound form

	context = {'form': form}
	return render(request, 'premik.html', context)