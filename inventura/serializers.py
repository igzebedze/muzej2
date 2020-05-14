from rest_framework import serializers
from .models import Eksponat, Primerek, Razstava, Kategorija

class KategorijaSerializer(serializers.ModelSerializer):
	eksponatov = serializers.SerializerMethodField()
	class Meta:
		model = Kategorija
		fields = ['ime','opis','eksponatov']
	def get_eksponatov(self, obj):
		return obj.eksponat_set.count()

class EksponatSerializer(serializers.ModelSerializer):
	proizvajalec = serializers.StringRelatedField()
	kategorija = serializers.StringRelatedField()
	class Meta:
		model = Eksponat
		fields = ['ime', 'tip', 'proizvajalec', 'opis', 'kategorija', 'wikipedia', 'oldcomputers', 'uradnastran', 'vir', 'onlinephoto']

class PrimerekSerializer(serializers.ModelSerializer):
	eksponat = EksponatSerializer(read_only=True)
	povezani = serializers.StringRelatedField(many=True)
	class Meta:
		model = Primerek
		fields = ('inventarna_st', 'eksponat', 'serijska_st', 'leto_proizvodnje', 'stanje', 'zgodovina', 'fotografija', 'povezani')

class RazstavaSerializer(serializers.ModelSerializer):
	primerki = PrimerekSerializer(many=True)
	avtorji = serializers.StringRelatedField(many=True)
	class Meta:
		model = Razstava
		fields = ['pk', 'primerki','naslov','lokacija','otvoritev','zakljucek','avtorji','opis']

