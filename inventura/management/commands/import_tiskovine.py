from django.core.management.base import BaseCommand, CommandError
import csv
import re
from inventura.models import Eksponat, User,  Lokacija, Tiskovina
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
	help = 'imports list of joker scans from server'

	def add_arguments(self, parser):
		parser.add_argument('file', nargs='+', type=str)

	def handle(self, *args, **options):
		pp = pprint.PrettyPrinter(indent=4)

		user = User.objects.get(pk=5)

		with open(options['file'][0]) as csvfile:
			reader = csv.DictReader(csvfile, delimiter='\t', quoting=csv.QUOTE_NONE)
			#headers = next(reader, None)
			lokacija = Lokacija.objects.get(ime='Spletni streznik')
			baseurl = 'https://revije.muzej.si/'

			for row in reader:
				dir = row['dir']
				pdf = baseurl + dir + '/' + row['pdf']
				cover = baseurl + dir + '/' + row['cover']
				pages = row['pages']
				eksponat = Eksponat.objects.get(tip=dir)	# warning - need to adjust the production settings

				# Joker_St-52_1997-11.pdf
				# BIT-1984-09/00000000.jpg
				# BIT-1984-09.pdf
				# z = re.match(".*Joker_St-(\d+)_(\d+)-(\d+)\.pdf", pdf)
				# Novice_1972_07.pdf
				# Novice_1978_12_18.pdf
				# informatica-Vol_23,_No_3_1999.pdf 
				# UI-1-1993.pdf
				patterns = (
					".*(\d\d\d\d)[-_](\d+)\.pdf",	# generic
					".*(\d\d\d\d)[-_](\d+)_\d\d\.pdf", # ijs exact date format
					".*(\d+)[-_](\d\d\d\d)\.pdf",	# informatica month+year last format
					".*(\d\d\d\d)\.pdf",	# only year, at the end
				)
				print("trying: " + pdf)
				for pattern in patterns:
					z = re.match(pattern, pdf)
					if z:
						if len(z.groups()) == 1:
							year = z.group(1)
							date = '%s-%s-%s' % (year, 1, 1)
							month = False
						elif len(z.groups()) == 2:
							a = int(z.group(1))
							b = int(z.group(2))
							year = max(a,b)
							month = min(a,b)
							if int(month) > 12:
								month = 1
							date = '%s-%s-%s' % (year, month, 1)

						t, created = Tiskovina.objects.get_or_create(
							pdf=pdf,
							naslovnica=cover,
							pages=int(pages),
							eksponat=eksponat,
						)
						if year:
							t.leto = int(year)
						if month:
							t.mesec = int(month)
						if date:
							t.datum = date
						t.save()
						print ('success: ' + pdf)
						continue
					