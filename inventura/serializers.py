from rest_framework import serializers
from .models import Eksponat, Primerek

class HeroSerializer(serializers.HyperlinkedModelSerializer):
	#eksponat = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
	class Meta:
		model = Primerek
		fields = ('inventarna_st', 'eksponat_name', 'serijska_st', 'leto_proizvodnje', 'stanje', 'zgodovina', 'fotografija', 'povezani')
        
