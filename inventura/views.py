import re

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.http import Http404
from django import forms
from django.views.generic import ListView, DetailView

from inventura.models import Vhod, Primerek, Lokacija, Izhod, Eksponat, Kategorija, Razstava, Proizvajalec

def root(request):
	return redirect('/admin/')

class PrimerekList(ListView):
	model = Primerek

class KategorijaList(ListView):
	model = Kategorija

class EksponatView(DetailView):
	model = Eksponat

class RazstavaView(DetailView):
	model = Razstava

def HomeView(request):
	context = {
		'razstave': Razstava.objects.order_by('-otvoritev'),
		'novosti': Primerek.objects.order_by('-datum_inventarizacije')[0:10]	
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
			'primerki_vhod_ja': Primerek.objects.filter(vhodni_dokument__isnull=False).count(),
			'primerki_vhod_ne': Primerek.objects.exclude(vhodni_dokument__isnull=False).count(),
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