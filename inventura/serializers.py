from rest_framework import serializers
from .models import Eksponat, Primerek

class HeroSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Primerek
        fields = ('eksponat', 'leto_proizvodnje')
        
