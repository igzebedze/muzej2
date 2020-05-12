import re
import wikipedia
import wptools
import wikitextparser as wtp
import urllib.parse
import random
import os.path
import pprint

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.http import Http404
from django import forms
from django.views.generic import ListView, DetailView
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.shortcuts import redirect

from .serializers import HeroSerializer
from rest_framework import viewsets, generics

from inventura.models import Vhod, Primerek, Lokacija, Izhod, Eksponat, Kategorija, Razstava, Proizvajalec

class HeroViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Primerek.objects.all()
    serializer_class = HeroSerializer
    
class iskalnik(viewsets.ModelViewSet):
    serializer_class = HeroSerializer

    def get_queryset(self):
        """
        Optionally restricts the returned purchases to a given user,
        by filtering against a `username` query parameter in the URL.
        """
        queryset = Primerek.objects.all()
        kveri = self.request.query_params.get('kveri', None)
        if kveri is not None:
            queryset = queryset.filter(eksponat__ime__icontains=kveri)
        return queryset

@login_required
def update_infobox(request, pk=None):
	e = Eksponat.objects.get(id=pk)
	
	# if this is a POST request we need to process the form data
	if request.method == 'POST':
		if 'wikiurl' in request.POST:
			wikiurl = urllib.parse.unquote(request.POST.get('wikiurl'))
			e.wikipedia = wikiurl
		if 'wikiimage' in request.POST:
			wikiimage = urllib.parse.unquote(request.POST.get('wikiimage'))
			e.onlinephoto = wikiimage
		if 'infobox' in request.POST:
			infobox = urllib.parse.unquote(request.POST.get('infobox'))
			e.infobox = infobox
		e.save()
			
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
					primerek = Primerek.objects.get(pk=id)
					primerki.append(primerek)
				except Primerek.DoesNotExist:
					messages.add_message(request, messages.ERROR,
							"Ne najdem primerka %d!" % (id,))

			print (primerki)
			context = { 'object_list': primerki }
			return render(request, 'listki.html', context)
	
	else:
		form = ListkiForm() # An unbound form
		
	context = {'form': form}
	return render(request, 'listkiform.html', context)	

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

		w = e.wikipedia
# if we don't have wiki page yet, search api for the object
		if not e.wikipedia or not e.onlinephoto:
			search = e.ime # e.proizvajalec.ime + " " + 
			#if e.tip:
			#	search = search + " " + e.tip
			search = search.replace("tipkovnica", "keyboard")
			search = search.replace("usmerjevalnik", "router")
			search = search.replace("kasetar", "casette player")
			search = search.replace("miška", "mouse")
			search = search.replace("ZDA", "USA")
			print ('checking: ' + search)
			try:
				pages = wikipedia.search(search, results=5)
				print (pages)
				#wiki = wikipedia.page(wikipedia.search(search, results=1))
			except:
				print ('blah: ' + search)
			else:
				context['wiki'] = []
				for p in pages:
					try:
						page = wikipedia.page(p)
						#pp = pprint.PrettyPrinter(indent=4)
						#pp.pprint (page)
					except:
						pass
					else:
						wiki = {'save': False}
						save = False
						if not e.wikipedia:
							wiki['wikiurl'] = page.url
							#pp.pprint (page.url)
							wiki['wikiname'] = page.title
							save = True
						try:
							if not e.onlinephoto:
								wiki['wikiimage'] = page.images[0]
								wiki['wikiimages'] = page.images[0,5]
								save = True
						except:
							pass
						
						if save:
							context['wiki'].append(wiki)
							#print (wiki)

# parse the data and store it
		if w and not e.infobox:
			slug = w.rsplit('/', 1)[-1]		# we only accept well formed wiki urls
			wiki = wptools.page(slug)
			try:
				page = wiki.get_restbase('/page/html/').data['html']
			except:
				pass
			else:
				infobox = re.findall("<table class=\"infobox.*?<\/table>", page)
				if infobox:
					context['infobox'] = "\n<br>\n".join(infobox)
		
		return context

class RazstavaView(DetailView):
	model = Razstava

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
	kategorije = {}
	
	for p in Proizvajalec.objects.all():
		drzave[p.drzava] = 1
	
	for e in Eksponat.objects.all():
		if e.proizvajalec:
			drzave[e.proizvajalec.drzava] = drzave[e.proizvajalec.drzava] + 1
	
	context = {
			'primerki_vhod_ja': Primerek.objects.filter(eksponat__isnull=False, vhodni_dokument__isnull=False).count(),
			'primerki_vhod_ne': Primerek.objects.exclude(eksponat__isnull=False, vhodni_dokument__isnull=False).count(),
			'eksponati_kategorije': Kategorija.objects.all(),
			'eksponati_drzave': drzave,
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