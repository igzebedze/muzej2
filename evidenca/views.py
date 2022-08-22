from django.shortcuts import render
from django.views.generic import ListView, DetailView
from evidenca.models import *

class RacunalnikListView(ListView):
    model=racunalnik
    queryset=racunalnik.objects.order_by('nakup')

class RacunalnikDetailView(DetailView):
    model=racunalnik

class OrganizacijeListView(ListView):
    model=organizacija
    queryset=organizacija.objects.order_by('ime')