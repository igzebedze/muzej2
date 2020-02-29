from django.core.management.base import BaseCommand, CommandError
import csv
import os
import sys
from django.utils import timezone
from inventura.models import Eksponat, Primerek, User, Kategorija, Proizvajalec
import pprint

class Command(BaseCommand):
	help = 'imports equipment list'

	def add_arguments(self, parser):
		parser.add_argument('file', nargs='+', type=str)

	def handle(self, *args, **options):
		pp = pprint.PrettyPrinter(indent=4)

		user = User.objects.get(pk=5)	# default user, will get overwritten

		start_no = 40000
		max = Primerek.objects.filter(inventarna_st__gte=start_no, inventarna_st__lt=50000).order_by('-inventarna_st')
		if max:
			start_no = max[0].inventarna_st + 1
		self.stdout.write("starting with number %d" % (start_no))
		
#navodila,,inv st,vrsta,vrednost [usd],leto,ime,lokacija,stanje,zgodovina,število delov,popisovalec
#kategorije:,,40000,pohistvo,14,2019,zlozljiv skerjanc stol bas natur,nadstropje,nov,posodil ustvarjalnik,1,bostjan

		with open(options['file'][0]) as csvfile:
			reader = csv.DictReader(csvfile)
			#headers = next(reader, None)
			for row in reader:
				inv_st = row['inv st']
				letnik = row['leto']
				ime = row['ime']
				self.stdout.write("looking at %s %s %s" % (ime, inv_st, letnik))
				kategorija = row['vrsta'].capitalize()
				drzava = "NN"				

				try:
					popisovalec = row['popisovalec']
					u = User.objects.get(username=popisovalec)
				except:
					pass
				else:
					user = u
			
				try: 
					stanje = row['stanje']
					zgodovina = row['zgodovina']
					p = Primerek.objects.get(inventarna_st=inv_st)
				except:
					p = Primerek(
								inventarna_st = inv_st,
								polica = row['lokacija'],
								serijska_st = "%s: %s" % (kategorija, ime),
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
#					start_no = start_no + 1
					self.stdout.write ("\tcreated new primerek for %s %s" % (inv_st, ime))
				else:
					self.stdout.write("\tskipping %s %s" % (inv_st, ime))
					pass
