from django.core.management.base import BaseCommand, CommandError
import re
import os
from inventura.models import Eksponat, User,  Lokacija, Tiskovina, Stran
import pprint

'''
class Tiskovina(models.Model):
	stevilka = models.IntegerField(blank=True, null=True, help_text='ce obstaja')
	leto = models.IntegerField(blank=True, null=True, help_text='priporoceno')
	mesec = models.IntegerField(blank=True, null=True, help_text='priporoceno')
	datum = models.DateField(blank=True, null=True, help_text='ce ni stevilke')
	besedilo = models.TextField(blank=True, null=True)
	kazalo = models.TextField(blank=True, null=True)
	naslovnica = models.URLField(blank=True, null=True)
	pdf = models.URLField(blank=True, null=True)
	pages = models.IntegerField(blank=True, null=True)
	primerek = models.ForeignKey(Primerek, blank=True, null=True, on_delete=models.PROTECT)
	eksponat = models.ForeignKey(Eksponat, on_delete=models.PROTECT)
'''

class Command(BaseCommand):
	help = 'imports pages of magazines from server'

	def add_arguments(self, parser):
		parser.add_argument('file', nargs='+', type=str)

	def handle(self, *args, **options):
		pp = pprint.PrettyPrinter(indent=4)
		user = User.objects.get(pk=5)
		baseurl = 'https://revije.muzej.si/'
		dir = options['file'][0].split('/')[-1]
# take dir from arguments, assume it is the magazine root
		for filename in os.listdir(options['file'][0]):
			if filename.endswith('.pdf'):
				revija = os.path.splitext(os.path.basename(filename))[0]
				pdf = baseurl + dir + '/' + revija + '.pdf'
				print (pdf)
				tiskovina = Tiskovina.objects.get(pdf=pdf)	

				for pagefile in os.listdir(options['file'][0] + '/' + revija):
					#print (pagefile)
					if pagefile.endswith('.txt') and (pagefile != ".txt") and not pagefile.endswith('.txt.txt'):
						stran = os.path.splitext(os.path.basename(pagefile))[0]
						#print (stran)

						vrsta = 'vsebina'
						k = re.compile(r'\bvsebina\b|\bkazalo\b|\bcontents\b', flags=re.I | re.X)

						with open(options['file'][0] + '/' + revija + '/' + pagefile, "r") as file:
							content = file.read()
							wordcount = len(content.split())
							if int(stran) == 0: 
								vrsta = 'naslovnica'
							elif k.match(content) and int(stran) < 6:
								vrsta = 'kazalo'
							elif wordcount < 100:
								vrsta = 'oglas'
							
							s, created = Stran.objects.get_or_create(
								tiskovina=tiskovina,
								stevilka = stran,
								slika = baseurl + dir + '/' + revija + '/' + stran + '.jpg'
							)
							if created:
								s.ocr = content
								s.vrsta = vrsta
								s.stevilo_besed = wordcount
								s.save()


# list all pdfs
# open folder with the same name
# list all jpg and txt files
# read txt files
# create pages
