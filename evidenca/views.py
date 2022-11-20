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

def stat(request):
	generacije = []	
	
	context = {
        'objekti': {
            'viri': vir.objects.count,
            'racunalniki': racunalnik.objects.count,
            'organizacije': organizacija.objects.count
        },
        'racunalniki': racunalnik.objects,
        'racunalniki_po_generacijah': generacije
	}
	return render(request, 'stat.html', context)
