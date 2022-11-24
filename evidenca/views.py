from django.shortcuts import render
from django.views.generic import ListView
from django.core import serializers
from evidenca.models import *
from rest_framework.decorators import api_view
from rest_framework.response import Response
from inventura.serializers import RacunalnikSerializer
from rest_framework import viewsets

class RacunalnikListView(ListView):
    model=racunalnik
    queryset=racunalnik.objects.order_by('nakup')

class RacunalnikiGeoJsonView(ListView):
    model=racunalnik
    queryset=racunalnik.objects.order_by('nakup')
    template_name='evidenca/racunalniki.geojson'

class OrganizacijeListView(ListView):
    model=organizacija
    queryset=organizacija.objects.order_by('ime')

class RacunalnikiGeoJsonView(ListView):
    model=racunalnik
    queryset=racunalnik.objects.order_by('nakup')
    template_name='evidenca/racunalniki.geojson'

@api_view(['GET', 'POST'])
def racunalnik_detail(request, pk):
    if request.method == 'GET':
        data = serializers.serialize("json", racunalnik.objects.all().prefetch_related().filter(pk=pk))
        # //serializer = RacunalnikSerializer(data, many=True)
        return Response(data)

def racunalnik_detail_rendered(request, pk):
    return render(request, 'evidenca/racunalnik_detail.html', {
        'racunalnik': racunalnik.objects.get(pk=pk),
    }, content_type='text/html')

class RacunalnikViewSet(viewsets.ReadOnlyModelViewSet):
	serializer_class = RacunalnikSerializer
	pagination_class = None
	queryset = racunalnik.objects.all().prefetch_related()

	def get_queryset(self):
		queryset = racunalnik.objects.all().prefetch_related()
		id = self.kwargs.get('pk', None)
		if id is not None:
			queryset = queryset.filter(pk=id)
		return queryset

