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
		kategorija = Kategorija.objects.get(ime="Revija")
		start_no = 10000
		max = Primerek.objects.filter(eksponat__kategorija=kategorija).order_by('-inventarna_st')
		if max:
			start_no = max[0].inventarna_st + 1
		self.stdout.write("starting with number %d" % (start_no))
		
		# revija,stevilka,leto,mesec,verzija,opombe
		# BIT,,1985,11,,
		with open(options['file'][0]) as csvfile:
			reader = csv.DictReader(csvfile)
			#headers = next(reader, None)
			for row in reader:
				if 'revija' not in row:
					continue

				letnik = row['leto']
				eksponat = row['revija']
				self.stdout.write("looking at %s %s" % (eksponat, letnik))
				vhod = ""#row['Zgodovina']

				if not eksponat:
					continue

				try:
					popisovalec = 'bostjan' #row['popisovalec']
					u = User.objects.get(username=popisovalec)
				except:
					pass
				else:
					user = u

				if 'Zgodovina' in row:
					v = row['Zgodovina']
					vhod = Vhod.objects.get(id=(int(v)))

				try:
					if eksponat=='Joker':
						e = Eksponat.objects.get(pk=465)	# we have two that need to be merged
					else:
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
					
				#months = list(row.values())[2:14]
				#self.stdout.write(pp.pformat(months))
				
				mesec = row['mesec']
				stevilka = row['stevilka']
				verzija = row['verzija']
				serijska = "%s-%s" % (letnik, mesec)
				
				if stevilka:
					serijska = "%s st. %s" % (serijska, stevilka)
				if verzija:
					serijska = "%s %s" % (serijska, verzija)

				try: 
							p = Primerek.objects.get(eksponat=e, serijska_st=serijska, leto_proizvodnje=int(letnik))
				except:
							p = Primerek(
								eksponat=e,
								inventarna_st = start_no,
								serijska_st = serijska,
								leto_proizvodnje = letnik,
								polica = "F3",
								inventariziral = user,
								datum_inventarizacije = timezone.now(),
								created_at = timezone.now(),
								updated_at = timezone.now()
							)
							if vhod:
								p.vhodni_dokument = vhod
							p.save()
							start_no = start_no + 1
							self.stdout.write ("created new primerek for %s %s" % (e, serijska))
				else:
							self.stdout.write("skipping %s %s" % (e, serijska))
							pass
