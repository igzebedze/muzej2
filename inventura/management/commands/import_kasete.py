from django.core.management.base import BaseCommand, CommandError
import csv
import os
import sys
from django.utils import timezone
from inventura.models import Eksponat, Primerek, User, Kategorija, Proizvajalec, Lokacija
import pprint

class Command(BaseCommand):
	help = 'imports list of kiberpipa video tapes'

	def add_arguments(self, parser):
		parser.add_argument('file', nargs='+', type=str)

	def handle(self, *args, **options):
		pp = pprint.PrettyPrinter(indent=4)

		user = User.objects.get(pk=5)
		kategorija = Kategorija.objects.get(ime="Video / Audio")

		start_no = 50000
		max = Primerek.objects.filter(eksponat__kategorija=kategorija).order_by('-inventarna_st')
		if max:
			start_no = max[0].inventarna_st + 1
		self.stdout.write("starting with number %d" % (start_no))

# Leto	Datum	Napis na kaseti	ostalo	Oseba	skatla		

		with open(options['file'][0]) as csvfile:
			reader = csv.DictReader(csvfile)
			#headers = next(reader, None)
			for row in reader:
# fixed
				eksponat = 'Kiberpipa kaseta' #row['eksponat'].capitalize()
				proizvajalec = 'Kiberpipa'
				user = User.objects.get(username='admin')
# input
				letnik = row['Leto']
				datum = row['Datum']
				napis = row['Napis na kaseti']
				opombe = row['ostalo']
				nastopajoci = row['Oseba']
				skatla = row['skatla']
# generated
				opis = "\n".join(["minidv kaseta posneta v Kiberpipi", row['Napis na kaseti'], row['Datum'], row['ostalo'], row['Oseba'], row['skatla']])
								
				self.stdout.write("looking at %s %s %s" % (proizvajalec, eksponat, letnik))

				if not eksponat:
					self.stdout.write("\tskipping")
					continue;

				try:
					m = Proizvajalec.objects.get(ime=proizvajalec)
				except:
					m = Proizvajalec(
						ime=proizvajalec,
						drzava="NN",
					)
					m.save()
					self.stdout.write("created new proizvajalec %s" % (m.ime))

				try:
					e = Eksponat.objects.get(ime=eksponat)
				except:
					e = Eksponat(
						ime=eksponat,
						proizvajalec=m,
						visina_cm = 5,
						dolzina_cm = 7,
						sirina_cm = 1,
						opis = opis,
						kategorija = kategorija,
						tip = "",
					)
					e.save()
					self.stdout.write ("created new eksponat for %s" % (e.ime))
# conditional			
				serijska = ""
				if 'Datum' in row:
					serijska = datum
				elif 'Leto' in row:
					serijska = letnik
	
				try: 
					p = Primerek.objects.get(eksponat=e, serijska_st=serijska, stanje=opis)
				except:
					p = Primerek(
								eksponat=e,
								inventarna_st = start_no,
								serijska_st = serijska,
								stanje = opis,
								polica = "skatla: %s" % (skatla),
								inventariziral = user,
#								zgodovina = row['zgodovina'],
#								lokacija = l,
#								stanje = "%s sekund\n%s\n%s" % (row['duration'], row['embed'], row['url']),
								datum_inventarizacije = timezone.now(),
								created_at = timezone.now(),
								updated_at = timezone.now()
							)
					if letnik:
						p.leto_proizvodnje = letnik
					p.save()
					start_no = start_no + 1
					self.stdout.write ("\tcreated new primerek for %s %s" % (e, serijska))
				else:
					self.stdout.write("\tskipping %s %s" % (e, serijska))
					pass
