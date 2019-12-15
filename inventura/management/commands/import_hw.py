from django.core.management.base import BaseCommand, CommandError
import csv
import os
import sys
from django.utils import timezone
from inventura.models import Eksponat, Primerek, User, Kategorija, Proizvajalec
import pprint

class Command(BaseCommand):
	help = 'imports hardware list'

	def add_arguments(self, parser):
		parser.add_argument('file', nargs='+', type=str)

	def handle(self, *args, **options):
		pp = pprint.PrettyPrinter(indent=4)

		user = User.objects.get(pk=5)	# default user, will get overwritten

		start_no = 1000
		max = Primerek.objects.filter(inventarna_st__gte=start_no, inventarna_st__lt=10000).order_by('-inventarna_st')
		if max:
			start_no = max[0].inventarna_st + 1
		self.stdout.write("starting with number %d" % (start_no))
		
# navodila,,vrsta,proizvajalec,ime,širina,dolžina,višina,leto,serijska številka,število delov,popisovalec,stanje,zgodovina,polica
# vrste eksponatov:,,Igralna konzola,Atari,Atari 2600,26,17,4,,A1 791400475,,marko,črna konzola s srebrno letvico z mavrico barv,zootfly,D1
		with open(options['file'][0]) as csvfile:
			reader = csv.DictReader(csvfile)
			#headers = next(reader, None)
			for row in reader:
				eksponat = row['ime'].capitalize()
				letnik = row['leto']
				proizvajalec = row['proizvajalec'].capitalize()
				self.stdout.write("looking at %s %s %s" % (proizvajalec, eksponat, letnik))
				kategorija = row['vrsta'].capitalize()
				
				# for no-name just use category name, i.e. "Monitor" 
				if not eksponat:
					eksponat = kategorija
				
				try:
					k = Kategorija.objects.get(ime=kategorija)
				except:
					k = Kategorija(
						ime = kategorija,
						opis = "ene sorte hardware",
					)
					k.save()
					self.stdout.write("\tcreated category %s" % (k.ime))					

				try:
					popisovalec = row['popisovalec']
					u = User.objects.get(username=popisovalec)
				except:
					pass
				else:
					user = u

				if not eksponat:
					continue;
					
				try:
					m = Proizvajalec.objects.get(ime=proizvajalec)
				except:
					m = Proizvajalec(
						ime=proizvajalec,
						drzava="NN",
					)
					m.save()
					self.stdout.write("\tcreated new proizvajalec %s" % (m.ime))

				v = row['višina']
				if not v:
					v = 1
				d = row['dolžina']
				if not d:
					d = 1
				s = row['širina']
				if not s:
					s = 1

				try:
					e = Eksponat.objects.get(ime=eksponat)
				except:
					e = Eksponat(
						ime=eksponat,
						proizvajalec=m,
						visina_cm = v,
						dolzina_cm = d,
						sirina_cm = s,
						opis = row['stanje'],
						kategorija = k,
						tip = "",
						created_at = timezone.now(),
						updated_at = timezone.now()
					)
					e.save()
					self.stdout.write ("\tcreated new eksponat for %s" % (e.ime))
			
				serijska = row["serijska številka"]	
				try: 
					stanje = row['stanje']
					zgodovina = row['zgodovina']
					p = Primerek.objects.get(eksponat=e, serijska_st=serijska, stanje=stanje, zgodovina=zgodovina)
				except:
					p = Primerek(
								eksponat=e,
								inventarna_st = start_no,
								serijska_st = serijska,
								polica = row['polica'],
								inventariziral = user,
								zgodovina = row['zgodovina'],
								stanje = row["stanje"],
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
