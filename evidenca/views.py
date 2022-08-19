from django.shortcuts import render
from django.views.generic import ListView
from evidenca.models import *

class RacunalnikListView(ListView):
    model = racunalnik

class OrganizacijeListView(ListView):
    model=organizacija