from rest_framework import serializers
from .models import Eksponat, Primerek, Razstava, Kategorija
from evidenca.models import racunalnik, organizacija

class KategorijaSerializer(serializers.ModelSerializer):
	eksponatov = serializers.SerializerMethodField()
	class Meta:
		model = Kategorija
		fields = ['ime','opis','eksponatov']
	def get_eksponatov(self, obj):
		counter = 0
		for eksponat in obj.eksponat_set.all():
			counter = counter + eksponat.primerek_set.count()
		return counter

class EksponatSerializer(serializers.ModelSerializer):
	proizvajalec = serializers.StringRelatedField()
	kategorija = serializers.StringRelatedField()
	class Meta:
		model = Eksponat
		fields = ['ime', 'tip', 'proizvajalec', 'opis', 'kategorija', 'wikipedia', 'oldcomputers', 'uradnastran', 'vir', 'onlinephoto']

class PrimerekSerializer(serializers.ModelSerializer):
	eksponat = EksponatSerializer(read_only=True)
	povezani = serializers.StringRelatedField(many=True)
	donator = serializers.SerializerMethodField()
	class Meta:
		model = Primerek
		fields = ('inventarna_st', 'eksponat', 'serijska_st', 'leto_proizvodnje', 'stanje', 'zgodovina', 'fotografija', 'povezani', 'donator')
	def get_donator(self, obj):
		if obj.vhodni_dokument and obj.vhodni_dokument.dovoli_objavo:
			return "%s (%s)" % (obj.vhodni_dokument.lastnik.ime, obj.vhodni_dokument.cas_prevzema.date())
		return ""

class RazstavaSerializer(serializers.ModelSerializer):
	primerki = PrimerekSerializer(many=True)
	avtorji = serializers.StringRelatedField(many=True)
	class Meta:
		model = Razstava
		fields = ['pk', 'primerki','naslov','lokacija','otvoritev','zakljucek','avtorji','opis']

class OrganizacijaSerializer(serializers.ModelSerializer):
	class Meta:
		model = organizacija
		fields = ['ime', 'naslov', 'url', 'povzetek', 'opis', 'podrocje', 'latlong']

class RacunalnikSerializer(serializers.ModelSerializer):
	nosilec = serializers.StringRelatedField()
	organizacija = OrganizacijaSerializer
	proizvajalec = serializers.StringRelatedField()
	eksponat = EksponatSerializer
	
	class Meta:
		model = racunalnik
		fields = ['nosilec', 'organizacija', 'tip', 'ime', 'uporaba', 'opombe', 'proizvajalec', 'eksponat', 'nakup', 'odpis', 'opis', 'generacija', 'viri', 'kraj', 'lastnistvo']
	def get_nosilec(self, obj):
		return({'ime': obj.organizacija.ime, 'pk': obj.organizacija.pk})