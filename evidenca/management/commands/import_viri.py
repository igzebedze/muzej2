from sre_constants import SRE_INFO_LITERAL
from django.core.management.base import BaseCommand, CommandError
import csv
import os
import sys
from django.utils import timezone
from evidenca.models import vir
import pprint

class Command(BaseCommand):
	help = 'imports master list of evidence sources'

	def add_arguments(self, parser):
		parser.add_argument('file', nargs='+', type=str)

	def handle(self, *args, **options):
		pp = pprint.PrettyPrinter(indent=4)
		
		with open(options['file'][0]) as csvfile:
			reader = csv.DictReader(csvfile)
			#headers = next(reader, None)
			for row in reader:
				if 'ŠIFRA' not in row:
					self.stdout.write('no sifra, skip')
					continue
				
				sifra = row['ŠIFRA']
				podrocje = row['VRSTA']
				naslov = row['ČLANEK']
				vsebina = row['VSEBINA']
				url = row['LINK']
				vrsta = 'clanek'

				leto = '19' + sifra[0:2]

				try:
					e = vir.objects.get(sifra=sifra)
					self.stdout.write ("found existing vir %s" % (sifra))
					#e.delete()
				except:
					e = vir(
						sifra=sifra,
                        naslov=naslov,
                        vsebina=vsebina,
                        url=url,
                        vrsta=vrsta,
						podrocje=podrocje						
					)
					e.save()

					try:
						datum = "%s-01-01" % (leto)
						e.datum = datum
						e.save()
					except:
						pass

					self.stdout.write ("created new vir for %s" % (e.naslov))
