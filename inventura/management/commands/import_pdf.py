from django.core.management.base import BaseCommand, CommandError
import csv
import os
import sys
from django.utils import timezone
from inventura.models import Eksponat, Primerek, User, Kategorija, Vhod
import pprint

class Command(BaseCommand):
	help = 'imports new editions of magazines'

	def add_arguments(self, parser):
		parser.add_argument('file', nargs='+', type=str)

	def handle(self, *args, **options):
		pp = pprint.PrettyPrinter(indent=4)

		user = User.objects.get(pk=5)
		start_no = 10000
		self.stdout.write("starting with number %d" % (start_no))
		
		# Moj mikro,1987,x,x,x,,x,x,x,,x,x,x,x
		with open(options['file'][0]) as csvfile:
			reader = csv.DictReader(csvfile, delimiter='\t')
			#headers = next(reader, None)
			
			max = Primerek.objects.filter(eksponat__kategorija=20).order_by('-inventarna_st')
			start_no = max[0].inventarna_st + 1
			
			for row in reader:
				if 'eksponat' not in row:
					continue

				kategorija = Kategorija.objects.get(ime=row['vrsta'])
				
				letnik = row['leto']
				eksponat = row['eksponat']
				serijska = row['serijska']
				fotografije = row['fotografije']
				self.stdout.write("looking at %s %s" % (eksponat, serijska))
#				vhod = row['Zgodovina']

				if not eksponat:
					continue

				try:
					popisovalec = 'igzebedze' #row['popisovalec']
					u = User.objects.get(username=popisovalec)
				except:
					pass
				else:
					user = u

#				if 'Zgodovina' in row:
#					v = row['Zgodovina']
#					vhod = Vhod.objects.get(id=(int(v)))

				try:
					e = Eksponat.objects.get(ime=eksponat)
				except:
					e = Eksponat(
						ime=eksponat,
						visina_cm = 1,
						dolzina_cm = 30,
						sirina_cm = 20,
						opis = "revija, ki je izhajala v sloveniji v slovenskem jeziku",
						kategorija = kategorija,
						tip = "",
					)
					e.save()
					self.stdout.write ("created new eksponat for %s" % (e.ime))
					
				try: 
					p = Primerek.objects.get(eksponat=e, serijska_st=serijska)
				except:
					p = Primerek(
								eksponat=e,
								inventarna_st = start_no,
								serijska_st = serijska,
								fotografije = fotografije,
								polica = "F3",
								inventariziral = user,
								datum_inventarizacije = timezone.now(),
								created_at = timezone.now(),
								updated_at = timezone.now()
							)
					if letnik:
						p.leto_proizvodnje = letnik
#					if vhod:
#								p.vhodni_dokument = vhod
					p.save()
					start_no = start_no + 1
					self.stdout.write ("created new primerek for %s %s" % (e, serijska))
				else:
					self.stdout.write("skipping %s %s" % (e, serijska))
					pass
