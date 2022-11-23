from django.shortcuts import render
from django.views.generic import ListView
from django.core import serializers
from evidenca.models import *
from rest_framework.decorators import api_view
from rest_framework.response import Response

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

# class RacunalnikSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = racunalnik
#         fields = ['pk', 'nosilec','organizacija','ime','tip','opombe','proizvajalec','nakup', 'opis', 'generacija', 'viri', 'kraj', 'lastnistvo']


@api_view(['GET', 'POST'])
def racunalnik_detail(request, pk):
    if request.method == 'GET':
        data = serializers.serialize("json", racunalnik.objects.all().prefetch_related().filter(pk=pk))
        # //serializer = RacunalnikSerializer(data, many=True)
        return Response(data)
