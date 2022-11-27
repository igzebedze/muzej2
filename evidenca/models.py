from random import choices
from django.db import models
from django.utils.html import format_html
from django.conf import settings

# Create your models here.
class vir(models.Model):
	VRSTA_CHOICES = (
			('clanek', 'clanek'),
			('knjiga', 'knjiga'),
            ('pogovor', 'pogovor'),
			('film', 'film'),
			('splet', 'splet')
	)
	VSEBINA_CHOICES = (
			('Seznam','Seznam'),
			('Javna uprava','Javna uprava'),
			('Zdravstvo','Zdravstvo'),
			('Šolstvo/Znanost','Šolstvo/Znanost'),
			('Domača izdelava','Domača izdelava'),
			('Programiranje','Programiranje'),
			('Splošno','Splošno'),
	)
	sifra = models.CharField(max_length=15, blank=True)
	url = models.URLField(blank=True, null=True,max_length=1000)
	vrsta = models.CharField(choices=VRSTA_CHOICES, max_length=255)
	podrocje = models.CharField(choices=VSEBINA_CHOICES, max_length=255, blank=True, null=True)
	naslov = models.TextField(blank=True)
	vsebina = models.TextField(blank=True)
	datum = models.DateField(blank=True, null=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	def __str__(self):
		return self.naslov

	def show_link(self):
		return format_html("<a href='{url}' target='_blank'>Vir</a>", url=self.url)

	class Meta:
		verbose_name_plural = "Viri"

class organizacija(models.Model):
	ime = models.CharField(max_length=255, blank=True)
	naslov = models.TextField(blank=True)
	url = models.URLField(blank=True, null=True)
	povzetek = models.TextField(blank=True)
	opis = models.TextField(blank=True)
	podrocje = models.CharField(blank=True, max_length=255)
	latlong=models.CharField(blank=True, max_length=255)
	partner = models.ManyToManyField("self", blank=True)
	predhodnik = models.ForeignKey("self", blank=True, null=True, on_delete=models.CASCADE)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	def __str__(self):
		return self.ime

	class Meta:
		verbose_name_plural = "Organizacije"


class racunalnik(models.Model):
	LASTNISTVO_CHOICES = (
		('L', 'lasten'),
		('N', 'najet'),
		('S', 'skupen'),
		('T', 'terminal'),
		('I', 'Izdelan doma')
	)
	TIP_CHOICES = (
		('ae','Analogni elektronski računalnik'),
		('e','Elektronski računalnik'),
		('t','Terminal'),
		('mg','Računski stroj (mehanografski)'),
		('emg', 'Elektronski računski stroj (mehanografski)'),
		('E', 'Največji računalnik v Jugoslaviji ob namestitvi'),
		('me', 'Mini računalnik, birojski/poslovni računalnik'),
		('pe', 'Procesni računalnik'),
		('mic', 'Mikro računalnik (domači/osebni/ostali)'),
		('cal', 'Programabilni kalkulator')
	)
	GENERACIJA_CHOICES = (
		('A','Predgeneracija računskih strojev (releji + vakuumske elektronke)'),
		('B','Prva generacija elektronskih računalnikov (vakuumske elektronke)'),
		('C','Druga generacija elektronskih računalnikov (tranzistorji)'),
		('D','Druga generacija elektronskih računalnikov (hibridna vezja in tranzistorji)'),
		('E','Tretja generacija elektronskih računalnikov (integrirana vezja in MOSFET)'),
		('F','Četrta generacija mikro računalnikov (mikroprocesorji)'),
		('G','Analogni in hibridni računalniki ()'),
		('X','Zelo šibki in pomanjkljivi viri ()')
	)
	UPORABA_CHOICES = (
		('J','Javna uprava'),
		('R','Znanstveno-raziskovalna dejavnost'),
		('Z','Zdravstvo'),
		('P','Poslovna dejavnost'),
		('Y','Jugoslavija'),
		('T','Bolj tuj kot domač'),
		('D','Bolj domač kot tuj'),
		('o', 'neznano')
	)

	kos = models.SmallIntegerField(default=1)
	nosilec = models.ForeignKey(organizacija, on_delete=models.CASCADE,related_name='nosilec', null=True)
	organizacija = models.ManyToManyField(organizacija, related_name='clan')
	ime = models.CharField(max_length=255, blank=True)
	tip = models.CharField(max_length=255, blank=True, choices=TIP_CHOICES)
	uporaba = models.CharField(max_length=255, blank=True, null=True, choices=UPORABA_CHOICES)
	opombe = models.TextField(blank=True, null=True)
	proizvajalec = models.ForeignKey('inventura.proizvajalec', on_delete=models.PROTECT)
	eksponat = models.ForeignKey('inventura.eksponat', blank=True, null=True, on_delete=models.PROTECT)
	nakup = models.DateField(blank=True, null=True)
	odpis = models.DateField(blank=True, null=True)
	opis = models.TextField(blank=True)
	generacija = models.CharField(choices=GENERACIJA_CHOICES, max_length=255, blank=True, null=True)
	viri = models.ManyToManyField(vir, blank=True)
	kraj = models.CharField(max_length=255, blank=True, null=True)
	lastnistvo = models.CharField(choices=LASTNISTVO_CHOICES, max_length=255, blank=True, null=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	def __str__(self):
		return "%s, %s (%s)" % (self.ime, self.nosilec, self.nakup.year)

	class Meta:
		verbose_name_plural = "Racunalniki"


class sluzba(models.Model):
	organizacija = models.ForeignKey(organizacija, blank=True, null=True, on_delete=models.PROTECT)
	od = models.DateField(blank=True, null=True)
	do = models.DateField(blank=True, null=True)
	naziv = models.CharField(max_length=255, blank=True)
	opis = models.TextField(blank=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	def __str__(self):
		if self.organizacija and self.od and self.do:
			return '%s %s %s-%s' % (self.naziv, self.organizacija.ime, self.od.year, self.do.year)
		elif self.organizacija and self.od:
			return '%s %s %s-' % (self.naziv, self.organizacija.ime, self.od.year)
		elif self.organizacija:
			return '%s %s' % (self.naziv, self.organizacija.ime)
		else:
			return ''

	class Meta:
		verbose_name_plural = "Sluzbe"


class dosezek(models.Model):
	VRSTA_CHOICES = (
		('konferenca','konferenca'),
		('hardware','hardware'),
		('software','software'),
		('publikacija','publikacija'),
		('podjetje','podjetje'),
		('drugo', 'drugo')
	)
	POMEN_CHOICES = (
		(1,'prelomno'),
		(2,'visoko'),
		(3,'posebno'),
	)
	ime = models.CharField(max_length=255, blank=True)
	povzetek = models.TextField(blank=True)
	opis = models.TextField(blank=True)
	url = models.URLField(blank=True, null=True)
	racunalnik = models.ManyToManyField(racunalnik, blank=True)
	od = models.DateField(blank=True, null=True)
	do = models.DateField(blank=True, null=True)
	vrsta = models.CharField(max_length=255, blank=True, choices=VRSTA_CHOICES)
	pomen = models.IntegerField(blank=True, default=3, choices=POMEN_CHOICES)
	eksponat = models.ManyToManyField('inventura.eksponat', blank=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	def __str__(self):
		return self.ime

	class Meta:
		verbose_name_plural = "Dosezki"


class oseba(models.Model):
	GENDER_MALE = 0
	GENDER_FEMALE = 1
	GENDER_CHOICES = [(GENDER_MALE, 'Moški'), (GENDER_FEMALE, 'Ženska')]

	ime = models.CharField(max_length=255, blank=True)
	url = models.URLField(blank=True, null=True, help_text="domača stran")
	wiki_sl = models.URLField(blank=True, null=True, help_text="<a target='_blank' href='https://sl.wikipedia.org/wiki/Glavna_stran'>slovenska wikipedia</a>")
	wiki_en = models.URLField(blank=True, null=True, help_text="<a target='_blank' href='https://en.wikipedia.org/wiki/Main_Page'>angleška wikipedia</a>")
	linkedin = models.URLField(blank=True, null=True, help_text="<a target='_blank' href='https://www.linkedin.com'>linkedin</a>")
	slobio = models.URLField(blank=True, null=True, help_text="<a target='_blank' href='https://www.slovenska-biografija.si'>slovenska biografija</a>")
	povzetek = models.TextField(blank=True)
	opis = models.TextField(blank=True)
	rojstvo = models.DateField(blank=True, null=True)
	smrt = models.DateField(blank=True, null=True)
	spol = models.IntegerField(choices=GENDER_CHOICES, default=0)
	sluzba = models.ManyToManyField(sluzba, blank=True)
	dosezek = models.ManyToManyField(dosezek, blank=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	def __str__(self):
		return self.ime

	class Meta:
		verbose_name_plural = "Osebe"
		ordering = ['ime']

class pogovor(models.Model):
	oseba = models.ForeignKey(oseba, on_delete=models.PROTECT)
	avtor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, default=17)
	datum = models.DateField()
	video = models.URLField(blank=True, null=True)
	audio = models.URLField(blank=True, null=True)
#	video = models.FileField(upload_to='pogovori', blank=True, null=True)
#	audio = models.FileField(upload_to='pogovori', blank=True, null=True)
	finalaudio = models.URLField(blank=True, null=True)
	finalvideo = models.URLField(blank=True, null=True)
	prepis = models.TextField(blank=True)
	zapiski = models.TextField(blank=True)
	url = models.URLField(blank=True, null=True)
	za_objavo = models.BooleanField(default=False)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	def __str__(self):
		return self.oseba.ime

	class Meta:
		verbose_name_plural = "Pogovori"
