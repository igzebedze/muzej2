from django.core.management.base import BaseCommand, CommandError
import csv
import os
import sys
from django.utils import timezone
from inventura.models import Eksponat, Primerek, User, Kategorija, Proizvajalec, Lokacija
import pprint

class Command(BaseCommand):
	help = 'imports list of video and audio files'

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
		
#eksponat	primerek	embed	url	id	duration	date	year
#Resnična resničnost	74. oddaja (2001)	https://4d.rtvslo.si/embed/174481907	https://4d.rtvslo.si/arhiv/resnicna-resnicnost/174481907	174481907	2117	2017-01-01	2001

		with open(options['file'][0]) as csvfile:
			reader = csv.DictReader(csvfile)
			#headers = next(reader, None)
			for row in reader:
				eksponat = row['eksponat'].capitalize()
				letnik = row['year']
				lokacija = 'Spletni streznik'
				proizvajalec = row['proizvajalec'].capitalize()
				self.stdout.write("looking at %s %s %s" % (proizvajalec, eksponat, letnik))

				try:
					popisovalec = row['popisovalec']
					u = User.objects.get(username=popisovalec)
				except:
					pass
				else:
					user = u

				if not eksponat:
					continue;

				l = Lokacija.objects.get(ime=lokacija)

				try:
					m = Proizvajalec.objects.get(ime=proizvajalec)
				except:
					m = Proizvajalec(
						ime=proizvajalec,
						drzava="NN",
					)
					m.save()
					self.stdout.write("created new proizvajalec %s" % (m.ime))

				opis = "oddaja ali posnetek"
				if 'description' in row:
					opis = row['description']

				try:
					e = Eksponat.objects.get(ime=eksponat)
				except:
					e = Eksponat(
						ime=eksponat,
#						proizvajalec=m,
						visina_cm = 1,
						dolzina_cm = 1,
						sirina_cm = 1,
						opis = opis,
						kategorija = kategorija,
						tip = "",
					)
					e.save()
					self.stdout.write ("created new eksponat for %s" % (e.ime))
			
				serijska = "%s" % (row['primerek'].capitalize())
				if "id" in row and row['id']:
					serijska = serijska + " (%s)" % (row['id'])
				if 'date' in row:
					serijska = serijska + " (%s)" % (row['date'])
	
				try: 
					p = Primerek.objects.get(eksponat=e, serijska_st=serijska)
				except:
					p = Primerek(
								eksponat=e,
								inventarna_st = start_no,
								serijska_st = serijska,
#								polica = row['polica'],
								inventariziral = user,
#								zgodovina = row['zgodovina'],
								lokacija = l,
								stanje = "%s sekund\n%s\n%s" % (row['duration'], row['embed'], row['url']),
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
