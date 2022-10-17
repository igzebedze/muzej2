from django.db import models
from django.utils.html import format_html
from django.conf import settings

# Create your models here.
class vir(models.Model):
	VRSTA_CHOICES = (
			('clanek', 'clanek'),
			('knjiga', 'knjiga'),
            ('pogovor', 'pogovor'),
			('film', 'film')
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
	partner = models.ManyToManyField("self", blank=True, null=True)
	predhodnik = models.ForeignKey("self", blank=True, null=True, on_delete=models.CASCADE)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	def __str__(self):
		return self.ime

	class Meta:
		verbose_name_plural = "Organizacije"


class racunalnik(models.Model):
	LASTNISTVO_CHOICES = (
		('lasten', 'lasten'),
		('najet', 'najet'),
		('skupen', 'skupen'),
		('PREVERI', 'PREVERI'),
		('odkup', 'odkup'),
		('terminal', 'terminal'),
		('prodan', 'prodan'),
		('oddan', 'oddan'),
		('zanimanje', 'zanimanje')
	)
	TIP_CHOICES = (
		('ae','analogen elektronski'),
		('e','elektronski'),
		('t','terminal'),
		('mg','mehanografski'),
		('pe','procesni elektronski')
	)
	kos = models.SmallIntegerField(default=1)
	nosilec = models.ForeignKey(organizacija, on_delete=models.CASCADE,related_name='nosilec', null=True)
	organizacija = models.ManyToManyField(organizacija)
	ime = models.CharField(max_length=255, blank=True)
	tip = models.CharField(max_length=255, blank=True, choices=TIP_CHOICES)
	opombe = models.TextField(blank=True, null=True)
	proizvajalec = models.ForeignKey('inventura.proizvajalec', on_delete=models.PROTECT)
	eksponat = models.ForeignKey('inventura.eksponat', blank=True, null=True, on_delete=models.PROTECT)
	nakup = models.DateField(blank=True, null=True)
	odpis = models.DateField(blank=True, null=True)
	opis = models.TextField(blank=True)
	generacija = models.IntegerField(blank=True, null=True)
	viri = models.ManyToManyField(vir, blank=True, null=True)
	kraj = models.CharField(max_length=255, blank=True, null=True)
	lastnistvo = models.CharField(choices=LASTNISTVO_CHOICES, max_length=255, blank=True, null=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	def __str__(self):
		return "%s, %s (%s)" % (self.ime, self.nosilec, self.nakup.year)

	class Meta:
		verbose_name_plural = "Racunalniki"


class sluzba(models.Model):
	organizacija = models.ManyToManyField(organizacija)
	od = models.DateField(blank=True, null=True)
	do = models.DateField(blank=True, null=True)
	naziv = models.CharField(max_length=255, blank=True)
	opis = models.TextField(blank=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	def __str__(self):
		return self.naziv

	class Meta:
		verbose_name_plural = "Sluzbe"


class dosezek(models.Model):
	ime = models.CharField(max_length=255, blank=True)
	povzetek = models.TextField(blank=True)
	opis = models.TextField(blank=True)
	url = models.URLField(blank=True, null=True)
	racunalnik = models.ManyToManyField(racunalnik, blank=True, null=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	def __str__(self):
		return self.ime

	class Meta:
		verbose_name_plural = "Dosezki"


class oseba(models.Model):
	ime = models.CharField(max_length=255, blank=True)
	url = models.URLField(blank=True, null=True)
	povzetek = models.TextField(blank=True)
	opis = models.TextField(blank=True)
	rojstvo = models.DateField(blank=True, null=True)
	smrt = models.DateField(blank=True, null=True)
	sluzba = models.ForeignKey(sluzba, blank=True, null=True, on_delete=models.PROTECT)
	dosezek = models.ManyToManyField(dosezek, blank=True, null=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	def __str__(self):
		return self.ime

	class Meta:
		verbose_name_plural = "Osebe"

class pogovor(models.Model):
	oseba = models.ForeignKey(oseba, on_delete=models.PROTECT)
	avtor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, default=17)
	datum = models.DateField()
	video = models.URLField(blank=True, null=True)
	audio = models.URLField(blank=True, null=True)
#	video = models.FileField(upload_to='pogovori', blank=True, null=True)
#	audio = models.FileField(upload_to='pogovori', blank=True, null=True)
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