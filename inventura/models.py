# -*- coding: utf-8 -*-

from django.db import models
from django.contrib.auth.models import User
from simple_history.models import HistoricalRecords
import os.path
import io
from PIL import Image
import datetime

from muzej2.settings import SLACKWEBHOOK, MEDIA_ROOT, MEDIA_URL
import requests
headers = {
    'Content-type': 'application/json',
}

class Search(models.Lookup):
    lookup_name = 'search'

    def as_mysql(self, compiler, connection):
        lhs, lhs_params = self.process_lhs(compiler, connection)
        rhs, rhs_params = self.process_rhs(compiler, connection)
        params = lhs_params + rhs_params
        return 'MATCH (%s) AGAINST (%s IN BOOLEAN MODE)' % (lhs, rhs), params

models.CharField.register_lookup(Search)
models.TextField.register_lookup(Search)

# curl -X POST -H 'Content-type: application/json' --data '{"text":"Hello, World!"}' https://hooks.slack.com/services/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

class Iskalnik(models.Model):
	vsebina = models.TextField()
	def __str__(self):
		return "%d" % (self.pk)

class Kveri(models.Model):
	kveri = models.CharField(max_length=255)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	def __str__(self):
		return self.kveri
	class Meta:
		verbose_name_plural = "Kveriji"
		
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

	dovoli_objavo = models.BooleanField(default=False, help_text="Darovalec dovoli objavo svojega imena na razstavah in javnih objavah.")

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
		
	def proizvajalci(self):
		list = {}
		for p in Proizvajalec.objects.all():
			eksponati = self.eksponat_set.filter(proizvajalec=p)
			if eksponati.count() > 0:
				list[p] = eksponati
		others = self.eksponat_set.filter(proizvajalec__isnull=True)
		list['neznani'] = others
		return list

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

	def st_eksponatov(self):
		return self.eksponat_set.count()

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
	infobox = models.TextField(blank=True, null=True, help_text="Infobox html iz Wikipedije")

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

# first check if we have thumbnail, 
# create thumbnails in process
	def fotografija(self):
		thumb_dir = MEDIA_ROOT + '/thumbs/'
		thumb_name = str(self.id) + ".png"

		if os.path.isfile(thumb_dir + thumb_name):
			return MEDIA_URL + 'thumbs/' + thumb_name
	
# then for uploaded pictures,		
		p = self.primerek_set.exclude(fotografija='')
		if p:
			with Image.open(p[0].fotografija.path) as im:
				im.thumbnail([250,250])
				im.save(thumb_dir + thumb_name)
			return MEDIA_URL + 'thumbs/' + thumb_name

# finally remote picture; 
		if self.onlinephoto:
			r = requests.get(self.onlinephoto, timeout=4.0)
			with Image.open(io.BytesIO(r.content)) as im:
				im.thumbnail([250, 250], Image.ANTIALIAS) # resizes 512x512 to 256x256
				im.save(thumb_dir + thumb_name)
			return MEDIA_URL + 'thumbs/' + thumb_name

		return ""

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
	
	iskalnik = models.ForeignKey(Iskalnik, blank=True, null=True, on_delete=models.SET_NULL)
	
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	def stevilka(self):
		return "%04d" % (self.inventarna_st,)
	stevilka.short_description = u'Številka'

	def __str__(self):
		return "#%d : %s" % (self.inventarna_st or 0, self.eksponat or '')

	def ima_vhod(self):
		if self.vhodni_dokument:
			return True
		else:
			return False

	def get_absolute_url(self):
		return "/admin/inventura/primerek/%d/" % (self.pk,)
		
	def eksponat_name(self):
		return "%s" % (self.eksponat.ime)
		
	def st_razstav(self):
		return "%d" % self.razstava_set.count()
	st_razstav.short_description = u'Št razstav'

	class Meta:
		verbose_name_plural = "Primerki"
		ordering = ['-leto_proizvodnje']

	def save (self, *args, **kw ):

# send slack notification for new objects 
		if not self.pk:	# if it's a new primerek
			data = "{'text':'nov primerek %s pod stevilko %s'}" % (self.eksponat, self.pk)
			data = data.encode('utf-8')
			response = requests.post(SLACKWEBHOOK, headers=headers, data=data)

# update search index
		fields = (self.serijska_st, self.stanje, self.zgodovina, self.eksponat.ime, self.eksponat.tip, self.eksponat.opis)
		vsebina = ' '.join(filter(None, fields))
		i = self.iskalnik
		try:
			i.vsebina = vsebina
			i.save()		
		except: 
			pass
			
		super( Primerek, self ).save( *args, **kw )

# note: it is possible to have an entry without actually having an object
class Tiskovina(models.Model):
	stevilka = models.IntegerField(blank=True, null=True)
	leto = models.IntegerField(blank=True, null=True)
	mesec = models.IntegerField(blank=True, null=True)
	datum = models.DateField(blank=True, null=True)
	besedilo = models.TextField(blank=True, null=True)
	kazalo = models.TextField(blank=True, null=True)
	naslovnica = models.ImageField(blank=True, null=True)
	pdf = models.URLField(blank=True, null=True)
	primerek = models.ForeignKey(Primerek, blank=True, null=True, on_delete=models.PROTECT)
	eksponat = models.ForeignKey(Eksponat, on_delete=models.PROTECT)

	dnevnik = HistoricalRecords()
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)	
	
	def __str__(self):
		stevilka = ""
		if self.stevilka:
			stevilka = self.stevilka
		elif self.leto and self.mesec:
			stevilka = "%s-%s" % (self.leto, self.mesec)
		elif self.datum:
			stevilka = "%s" % (self.datum)

		return "%s %s" % (self.eksponat, stevilka)
	class Meta:
		verbose_name_plural = "Tiskovine"
		
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
		
class Projekt(models.Model):
	nosilec = models.ForeignKey(User, on_delete=models.PROTECT,
			help_text="sodelavec muzeja, ki je glavni vir energije in/ali znanja")
	naslov = models.CharField(max_length=255)
	opis = models.TextField(blank=True, help_text="nekaj ozadja in motivacije")
	rezultat = models.TextField(blank=True, 
			help_text="zelo konkretno, kaj se bo videlo")
	datum = models.DateField(default=datetime.date.today)
	dokumentacija = models.URLField(blank=True, null=True)

	POTREBE_CHOICES = (
		('cas', 'cas'),
		('prostovoljci', 'prostovoljci'),
		('vodja', 'vodja'),
		('oprema', 'oprema'),
		('projekt', 'caka drug projekt')
	)
	VRSTA_CHOICES = (
		('javnost', 'dajanje na voljo javnosti'),
		('raziskovanje', 'raziskovanje'),
		('ohranjanje', 'ohranjanje predmetov'),
		('zbiranje', 'zbiranje'),
		('podpora', 'podpora organizaciji'),
		('izobrazevanje', 'izobrazevanje, delavnice'),
		('produkcija', 'produkcija, razvoj izdelkov, art')
	)
	STATUS_CHOICES = (
		('ideja', 'ideja'),
		('cakanje', 'cakanje'),
		('aktiven', 'aktiven'),
		('koncan', 'koncan'),
		('vzdrzevanje', 'vzdrzevanje')
	)
	status = models.CharField(choices=STATUS_CHOICES, max_length=255)
	potrebe = models.CharField(choices=POTREBE_CHOICES, max_length=255)
	vrsta = models.CharField(choices=VRSTA_CHOICES, max_length=255)

	dnevnik = HistoricalRecords()
	
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	def __str__(self):
		return self.naslov()

	class Meta:
		verbose_name_plural = "Projekti"
