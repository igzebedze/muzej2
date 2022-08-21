from sre_constants import SRE_INFO_LITERAL
from django.core.management.base import BaseCommand, CommandError
import csv
import os
import sys
from django.utils import timezone
from evidenca.models import racunalnik, organizacija, vir
from inventura.models import Proizvajalec
import pprint

class Command(BaseCommand):
	help = 'imports master list of historic computers'

	def add_arguments(self, parser):
		parser.add_argument('file', nargs='+', type=str)

	def handle(self, *args, **options):
		pp = pprint.PrettyPrinter(indent=4)
		
		with open(options['file'][0]) as csvfile:
			reader = csv.DictReader(csvfile)
			#headers = next(reader, None)
			for row in reader:
				if 'KOLICINA' not in row:
					self.stdout.write('no items, skip')
					continue
				
# LETO,KRAJ,PROIZVAJALEC,MODEL,OPOMBE,KOLICINA,TIP,LASTNIŠTVO,PODJETJE,VIRI
# 1946,Kranj,POWERS-SAMAS,POWERS-SAMAS London,,1,mg,lasten,Iskra Kranj,"57/01, 60/02, 65/01, 66/04"

				podjetja = row['PODJETJE'].split('+')
				tip = row['TIP']
				lastnistvo = row['LASTNIŠTVO']
				viri = row['VIRI'].split(',')
				opombe = row['OPOMBE']
				model = row['MODEL']
				proizvajalec = row['PROIZVAJALEC']
				kraj = row['KRAJ']
				leto = row['LETO']

				if not row['KOLICINA'] or row['KOLICINA'] == '':
					next	# skip rows without items
				else:
					kolicina=int(row['KOLICINA'])

				for v in viri:
					v.strip()
				for p in podjetja:
					p.strip()

				letnica = "%s-01-01" % (leto)
				p, created = Proizvajalec.objects.get_or_create(ime=proizvajalec)

				for i in range(kolicina):
					try:
						nosilec = podjetja[0].strip()
						n, created = organizacija.objects.get_or_create(ime=nosilec)
						if created:
							self.stdout.write("created new organization: %s" % (n))
						r, created = racunalnik.objects.get_or_create(
							ime=model,
							opombe=opombe,
							tip=tip,
							kraj=kraj,
							nakup=letnica,
							proizvajalec=p,
							nosilec=n,
							lastnistvo=lastnistvo,
							kos=(i+1)
						)
						if created:
							self.stdout.write("created new computer: %s" % (model))

					except Exception as e:
						self.stdout.write("error creating object: %s" % (e))

					else:
						for sifra in viri:
							sifra = sifra.strip()
							sifra = sifra.replace('*','')
							try:
								v = vir.objects.get(sifra=sifra)
							except Exception as e:
								self.stdout.write("source not found, skipping: '%s' - %s" % (sifra, e))
								pass
							else:
								r.viri.add(v)
						for org in podjetja:
							org = org.strip()
							o, created = organizacija.objects.get_or_create(ime=org)
							if created:
								self.stdout.write("created new org: %s" % (o))
							r.organizacija.add(o)

						r.save()
