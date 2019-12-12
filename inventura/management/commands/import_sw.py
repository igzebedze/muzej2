from django.core.management.base import BaseCommand, CommandError
import csv
import os
import sys
from django.utils import timezone
from inventura.models import Eksponat, Primerek, User, Kategorija, Proizvajalec
import pprint

class Command(BaseCommand):
	help = 'imports original software list'

	def add_arguments(self, parser):
		parser.add_argument('file', nargs='+', type=str)

	def handle(self, *args, **options):
		pp = pprint.PrettyPrinter(indent=4)

		user = User.objects.get(pk=5)
		kategorija = Kategorija.objects.get(ime="Programski paket")

		start_no = 20000
		max = Primerek.objects.filter(eksponat__kategorija=kategorija).order_by('-inventarna_st')
		if max:
			start_no = max[0].inventarna_st + 1
		self.stdout.write("starting with number %d" % (start_no))
		
		# vrsta,proizvajalec,program,verzija,leto,stanje,OS,medij,avtor
		# programska oprema,borland,quattro pro,1.0,1993,rabljeno,win,"5"" floppy",
		with open(options['file'][0]) as csvfile:
			reader = csv.DictReader(csvfile)
			#headers = next(reader, None)
			for row in reader:
				eksponat = row['vrsta'].capitalize()
				letnik = row['leto']
				proizvajalec = row['proizvajalec'].capitalize()
				self.stdout.write("looking at %s %s %s" % (proizvajalec, eksponat, letnik))

				popisovalec = row['popisovalec']
				if popisovalec:
					try:
						u = User.objects.get(username=popisovalec)
					except:
						pass
					else:
						user = u

				if not eksponat:
					continue;
					
#				try:
#					m = Proizvajalec.objects.get(ime=proizvajalec)
#				except:
#					m = Proizvajalec(
#						ime=proizvajalec,
#						drzava="NN",
#					)
#					m.save()
#					self.stdout.write("created new proizvajalec %s" % (m.ime))

				try:
					e = Eksponat.objects.get(ime=eksponat)
				except:
					e = Eksponat(
						ime=eksponat,
#						proizvajalec=m,
						visina_cm = 1,
						dolzina_cm = 1,
						sirina_cm = 1,
						opis = "ene sorte software",
						kategorija = kategorija,
						tip = "",
					)
					e.save()
					self.stdout.write ("created new eksponat for %s" % (e.ime))
			
				serijska = "%s %s" % (row['proizvajalec'].capitalize(), row['program'].capitalize())
				if row['verzija']:
					serijska = serijska + " %s" %(row['verzija'].capitalize())
				if row['OS']:
					serijska = serijska + " for %s" % (row['OS'].capitalize())
	
				try: 
					p = Primerek.objects.get(eksponat=e, serijska_st=serijska)
				except:
					p = Primerek(
								eksponat=e,
								inventarna_st = start_no,
								serijska_st = serijska,
								polica = "F5",
								inventariziral = user,
								zgodovina = row['avtor'],
								stanje = "%s\n%s" % (row['stanje'], row['medij']),
								datum_inventarizacije = timezone.now(),
								created_at = timezone.now(),
								updated_at = timezone.now()
							)
					if letnik:
						p.leto_proizvodnje = letnik
					p.save()
					start_no = start_no + 1
					self.stdout.write ("created new primerek for %s %s" % (e, serijska))
				else:
					self.stdout.write("skipping %s %s" % (e, serijska))
					pass
