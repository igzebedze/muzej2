# -*- coding: utf-8 -*-

from django.db import models
from django.contrib.auth.models import User
from simple_history.models import HistoricalRecords

from muzej2.settings import SLACKWEBHOOK
import requests
headers = {
    'Content-type': 'application/json',
}

# curl -X POST -H 'Content-type: application/json' --data '{"text":"Hello, World!"}' https://hooks.slack.com/services/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

class Lokacija(models.Model):
	ime = models.CharField(
			max_length=255)

	naslov = models.TextField(blank=True)
	
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	def __str__(self):
		return self.ime

	def st_primerkov(self):
		return "%d" % self.primerek_set.count()
	st_primerkov.short_description = u'Št primerkov'

	class Meta:
		verbose_name_plural = "Lokacije"

def get_default_lokacija():
	return Lokacija.objects.get(ime="Celovška 111")

class Oseba(models.Model):
	ime = models.CharField(
			max_length=255,
			help_text="za fizične osebe uporabi obliko \"priimek, ime\"")

	naslov = models.TextField(blank=True)
	telefon = models.CharField(max_length=255, blank=True)
	email = models.EmailField(blank=True, null=True)

	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	def __str__(self):
		return self.ime

	class Meta:
		verbose_name_plural = "Osebe"

class Vhod(models.Model):
	izrocitelj = models.ForeignKey(Oseba, blank=True, null=True, on_delete=models.PROTECT,
			related_name="izrocitelj",
			verbose_name="izročitelj",
			help_text="kdo je prinesel eksponat (če ni lastnik)")

	lastnik = models.ForeignKey(Oseba, on_delete=models.PROTECT,
			related_name="lastnik",
			help_text="kdo je trenutno lastnik eksponata")

	opis = models.TextField(
			help_text="kratek opis izročenih predmetov, stanje, vidne poškodbe, "
			"zgodovina predmeta")

	RAZLOG_CHOICES = (
			('dar', 'dar'),
			('izposoja', 'izposoja'),
	)

	razlog = models.CharField(choices=RAZLOG_CHOICES, max_length=255,
			help_text="razlog za sprejem eksponata")

	zacasna_lokacija = models.ForeignKey(Lokacija, on_delete=models.PROTECT,
			verbose_name="začasna lokacija",
			default=get_default_lokacija,
			blank=True, null=True)

	dogovorjeni_datum_vrnitve = models.DateField(blank=True, null=True)
	datum_vrnitve = models.DateField(blank=True, null=True,
			help_text="datum dejanske vrnitve")

	opombe = models.TextField(blank=True,
			help_text="podrobnosti glede vrnitve")

	prevzel = models.ForeignKey(User, on_delete=models.PROTECT,
			help_text="sodelavec muzeja, ki je prevzel eksponat")

	cas_prevzema = models.DateTimeField(verbose_name="čas prevzema")
	dnevnik = HistoricalRecords()
	
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)
    
	def stevilka(self):
		return "VH%05d" % (self.id,)
	stevilka.short_description = u'Številka'
    
	def inventorizirano(self):
		if Primerek.objects.filter(vhodni_dokument=self):
			return "da"
		else:
			return ""

	def __str__(self):
		return self.stevilka()

	def get_absolute_url(self):
		return "/vhod/%d/" % (self.id,)

	class Meta:
		verbose_name_plural = "Vhodi"

class Kategorija(models.Model):
	ime = models.CharField(max_length=255)
	opis = models.TextField()
	
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	def __str__(self):
		return self.ime

	class Meta:
		verbose_name_plural = "Kategorije"

class Proizvajalec(models.Model):
	ime = models.CharField(
			max_length=255)

	drzava = models.CharField(
			max_length=255,
			verbose_name="Država")

	ustanovljen = models.PositiveIntegerField(blank=True, null=True)
	propadel = models.PositiveIntegerField(blank=True, null=True)

	opis = models.TextField(blank=True)

	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	def __str__(self):
		return "%s, %s" % (self.ime, self.drzava)

	class Meta:
		verbose_name_plural = "Proizvajalci"

class Eksponat(models.Model):
	ime = models.CharField(
			max_length=255,
			help_text="obče izdelka, ki ga eksponat predstavlja")

	tip = models.CharField(
			max_length=255,
			blank=True, null=True,
			help_text="tovarniška oznaka, številka tipa")

	proizvajalec = models.ForeignKey(Proizvajalec, blank=True, null=True, on_delete=models.PROTECT)

	visina_cm = models.PositiveIntegerField(
			verbose_name="Višina [cm]")
	dolzina_cm = models.PositiveIntegerField(
			verbose_name="Dolžina [cm]")
	sirina_cm = models.PositiveIntegerField(
			verbose_name="Širina [cm]")

	opis = models.TextField(
			help_text="splošni opis izdelka, ki ga eksponat predstavlja, "
			"in se ne nanaša na specifični primerek (naj vsebuje najmanj "
			"fizični opis, po katerem je mogoče razpoznati eksponat: "
			"oblika, barva, ali je vgrajena tipkovnica, monitor, disketna "
			"enota, itd.)")

	kategorija = models.ForeignKey(Kategorija, on_delete=models.PROTECT)

	wikipedia = models.URLField(blank=True, null=True, help_text="Članek na katerikoli Wikipediji")
	oldcomputers = models.URLField(blank=True, null=True, help_text="Najbolj relevanten vir za dotično področje, na primer oldcomputers.net, atarimuseum, tomcat")
	uradnastran = models.URLField(blank=True, null=True, help_text="Uradna stran če še obstaja, npr IBM")
	vir = models.URLField(blank=True, null=True, help_text="kakršenkoli drug vir, npr Cobiss")
	onlinephoto = models.URLField(blank=True, null=True, help_text="Reprezentativna slika iz enega od zgornjih virov")

	dnevnik = HistoricalRecords()
	
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	def leto_proizvodnje(self):
		agg = self.primerek_set.aggregate(
				models.Min("leto_proizvodnje"), 
				models.Max("leto_proizvodnje"))

		leto_min = agg['leto_proizvodnje__min']
		leto_max = agg['leto_proizvodnje__max']

		if leto_min == leto_max:
			return str(leto_min)
		else:
			return "%d - %d" % (leto_min, leto_max) 

	def st_primerkov(self):
		return "%d" % self.primerek_set.count()
	st_primerkov.short_description = u'Št primerkov'

	def __str__(self):
		return self.ime

	def get_absolute_url(self):
		return "/eksponat/%d/" % (self.id,)

	class Meta:
		verbose_name_plural = "Eksponati"
		ordering = ['ime']

class Primerek(models.Model):
	inventarna_st = models.PositiveIntegerField(
			primary_key=True,
			verbose_name="Inventarna številka")

	eksponat = models.ForeignKey(Eksponat, blank=True, null=True, on_delete=models.PROTECT,
			help_text="pusti prazno, če gre za muzejsko opremo in ne eksponat")

	st_delov = models.PositiveIntegerField(
			default=1,
			verbose_name="Število delov",
			help_text="iz koliko delov je sestavljen primerek (vsak del ima "
			"svojo nalepko z inventarno št. in št. dela - npr. 12345/6)")

	serijska_st = models.CharField(
			max_length=255, blank=True,
			verbose_name="Serijska številka")

	leto_proizvodnje = models.PositiveIntegerField(blank=True, null=True)

	inventariziral = models.ForeignKey(
			User, on_delete=models.PROTECT,
			help_text="kdo je iz vhodnega dokumenta naredil kataloški vnos")

	datum_inventarizacije = models.DateTimeField(auto_now_add=True)

	stanje = models.TextField(
			blank=True,
			help_text="opis stanja (poškodbe, posebnosti, spremembe) in "
			"ostale opombe, specifične za ta primerek")

	zgodovina = models.TextField(
			blank=True, null=True,
			help_text="zgodovina primerka (zakaj se je uporabljal, kdo in kdaj)")

	donator = models.ForeignKey(
			Oseba, on_delete=models.PROTECT,
			blank=True,
			null=True,
			help_text="kdo je primerek podaril muzej")

	vrednost = models.PositiveIntegerField(
		default=0,
		verbose_name="Ocenjena vrednost v USD",
		help_text="ocenjena tržna vrednost (npr Ebay), upoštevajoč stanje primerka"
	)

	lokacija = models.ForeignKey(Lokacija, default=get_default_lokacija, on_delete=models.PROTECT)
	polica = models.CharField(
		max_length=255, blank=True, 
		verbose_name="polica, regal",
		help_text="čimbolj točna pozicija znotraj lokacije, npr: A-1.1 za prvo polico v skladišču"
	)
	
	fotografija = models.ImageField(upload_to='primerki', blank=True, null=True,
		help_text='vzorčna fotografija, ki se uporablja v spletnem katalogu'
	)
	fotografije = models.URLField(blank=True, null=True,
		help_text="spletno mesto kjer se hranijo fotografije, npr gdrive ali dropbox"
	)

	posegi = models.TextField(
		blank=True,
		help_text="dnevnik vseh premikov, čiščenj, popravil ipd."
	)

	povezani = models.ManyToManyField('self', blank=True, 
		help_text="drugi primerki, ki običajno potujejo skupaj. Npr: celoten računalnik z monitorjem in tipkovnico."
	)

	vhodni_dokument = models.ForeignKey(Vhod, blank=True, null=True, on_delete=models.PROTECT)
	dnevnik = HistoricalRecords()
	
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	def stevilka(self):
		return "%04d" % (self.inventarna_st,)
	stevilka.short_description = u'Številka'

	def __str__(self):
		return "#%d : %s" % (self.inventarna_st, self.eksponat)

	def get_absolute_url(self):
		return "/admin/inventura/primerek/%d/" % (self.pk,)
		
	def st_razstav(self):
		return "%d" % self.razstava_set.count()
	st_razstav.short_description = u'Št razstav'

	class Meta:
		verbose_name_plural = "Primerki"

	def save (self, *args, **kw ):
		if not self.pk:	# if it's a new primerek
			data = "{'text':'nov primerek %s pod stevilko %s'}" % (self.eksponat, self.pk)
			data = data.encode('utf-8')
			response = requests.post(SLACKWEBHOOK, headers=headers, data=data)
		super( Primerek, self ).save( *args, **kw )


class Razstava(models.Model):
	primerki = models.ManyToManyField(Primerek)
	naslov = models.CharField(max_length=255)
	lokacija = models.ForeignKey(Lokacija, on_delete=models.PROTECT)
	otvoritev = models.DateField(blank=True, null=True)
	zakljucek = models.DateField(blank=True, null=True)
	avtorji = models.ManyToManyField(Oseba)
	opis = models.TextField()
	dnevnik = HistoricalRecords()
	
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	def __str__(self):
		return "%s, %s, %s" % (self.naslov, self.lokacija, self.otvoritev)
	def get_absolute_url(self):
		return "/razstava/%d/" % (self.pk,)
	class Meta:
		verbose_name_plural = "Razstave"
    
class Pregled(models.Model):
	primerek = models.ForeignKey(Primerek, on_delete=models.PROTECT)
	izvajalec = models.ForeignKey(Oseba, on_delete=models.PROTECT)
	datum = models.DateTimeField()
	deluje = models.BooleanField(default=False)
	zapiski = models.TextField()
	dnevnik = HistoricalRecords()
	
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)
	
	def __str__(self):
		return "%s, %s, %s" % (self.primerek, self.datum, self.izvajalec)
	
	class Meta:
		verbose_name_plural = "Pregledi"
		
	def save (self, *args, **kw ):
		if not self.pk:	# if it's a new pregled
			data = "{'text':'%s je pregledal %s in odkril sledece: %s'}" % (self.izvajalec, self.primerek, self.zapiski)
			data = data.encode('utf-8')
			response = requests.post(SLACKWEBHOOK, headers=headers, data=data)
		super( Pregled, self ).save( *args, **kw )
    
class Izhod(models.Model):

	prevzemnik = models.ForeignKey(Oseba, blank=True, null=True, on_delete=models.PROTECT,
			related_name="prevzemnik",
			verbose_name="prevzemnik",
			help_text="komu izdajamo")

	ustanova = models.CharField(max_length=255, default="Posameznik")

	stanje = models.TextField(
		help_text="kratek opis izročenih predmetov, stanje, vidne poškodbe", 
	)

	nacin = models.TextField(
		help_text="Način prevzema"
	)

	primerki = models.ManyToManyField(Primerek)

	RAZLOG_CHOICES = (
			('dar', 'dar'),
			('izposoja', 'izposoja'),
            ('odpis', 'odpis')
	)

	namen = models.CharField(choices=RAZLOG_CHOICES, max_length=255,
			help_text="namen posoje eksponata, npr 'razstava' ali 'popravilo'")

	zacasna_lokacija = models.ForeignKey(Lokacija, on_delete=models.PROTECT,
			verbose_name="začasna lokacija",
			default=get_default_lokacija,
			blank=True, null=True)

	opombe = models.TextField(blank=True,
			help_text="podrobnosti glede vrnitve")

	izdal = models.ForeignKey(User, on_delete=models.PROTECT,
			help_text="sodelavec muzeja, ki je izdal eksponat")

	cas_prevzema = models.DateTimeField(verbose_name="čas prevzema")
	dogovorjeni_datum_vrnitve = models.DateField(blank=True, null=True)
	datum_vrnitve = models.DateField(blank=True, null=True,
			help_text="datum dejanske vrnitve")

	dnevnik = HistoricalRecords()
	
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	def stevilka(self):
		return "IZH%05d" % (self.id,)
	stevilka.short_description = u'Številka'

	def inventorizirano(self):
		if Primerek.objects.filter(izhodni_dokument=self):
			return "da"
		else:
			return ""

	def __str__(self):
		return self.stevilka()

	def get_absolute_url(self):
		return "/izhod/%d/" % (self.id,)

	class Meta:
		verbose_name_plural = "Izhodi"