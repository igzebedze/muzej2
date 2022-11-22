from django.shortcuts import render
from django.views.generic import ListView, DetailView
from evidenca.models import *

class RacunalnikListView(ListView):
    model=racunalnik
    queryset=racunalnik.objects.order_by('nakup')

class RacunalnikiGeoJsonView(ListView):
    model=racunalnik
    queryset=racunalnik.objects.order_by('nakup')
    template_name='evidenca/racunalniki.geojson'

class RacunalnikDetailView(DetailView):
    model=racunalnik

class OrganizacijeListView(ListView):
    model=organizacija
    queryset=organizacija.objects.order_by('ime')

class RacunalnikiGeoJsonView(ListView):
    model=racunalnik
    queryset=racunalnik.objects.order_by('nakup')
    template_name='evidenca/racunalniki.geojson'

