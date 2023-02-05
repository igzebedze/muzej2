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
				eksponat = Eksponat.objects.get(ime=dir)

				# Joker_St-52_1997-11.pdf
				# BIT-1984-09/00000000.jpg
				# BIT-1984-09.pdf
				# z = re.match(".*Joker_St-(\d+)_(\d+)-(\d+)\.pdf", pdf)
				z = re.match(".*(\d\d\d\d)-(\d+)\.pdf", pdf)

				if not z:
					print ("fail: " + pdf)
				else:
					year = z.group(1)
					month = z.group(2)
					date = '%s-%s-%s' % (year, month, 1)

					t, created = Tiskovina.objects.get_or_create(
						pdf=pdf,
						naslovnica=cover,
						pages=int(pages),
						leto = int(year),
						mesec = int(month),
						eksponat=eksponat,
						datum=date
					)

					print ('success: ' + pdf)