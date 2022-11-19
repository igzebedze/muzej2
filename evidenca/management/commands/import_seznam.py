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
				
# V1
# LETO,KRAJ,PROIZVAJALEC,MODEL,OPOMBE,KOLICINA,TIP,LASTNIŠTVO,PODJETJE,VIRI
# 1946,Kranj,POWERS-SAMAS,POWERS-SAMAS London,,1,mg,lasten,Iskra Kranj,"57/01, 60/02, 65/01, 66/04"

# V2
# GENERACIJA	ZAPOREDNI	KOLICINA	LETO	PROIZVAJALEC	MODEL	OPOMBE	TIP	UPORABA	LASTNISTVO	NOSILEC	KRAJ	PARTNER	DOSTOP	VIRI	

				nosilec = row['NOSILEC']
				partnerji = row['PARTNER'].split(',')
				uporabniki = row['DOSTOP'].split(',')
				tip = row['TIP']
				lastnistvo = row['LASTNISTVO']
				viri = row['VIRI'].split(',')
				opombe = row['OPOMBE']
				model = row['MODEL']
				proizvajalec = row['PROIZVAJALEC']
				kraj = row['KRAJ']
				leto = row['LETO']
				generacija = row['GENERACIJA']
				uporaba = row['UPORABA']

				if not row['KOLICINA'] or row['KOLICINA'] == '':
					next	# skip rows without items
				else:
					kolicina=int(row['KOLICINA'])

				for v in viri:
					v.strip()
				for p in partnerji:
					p.strip()
				for p in uporabniki:
					p.strip()

				letnica = "%s-01-01" % (leto)
				p, created = Proizvajalec.objects.get_or_create(ime=proizvajalec)

				if tip == 't':
					next	# skip terminals for now

				for i in range(kolicina):
					try:
						nosilec = nosilec.strip()
						n, created = organizacija.objects.get_or_create(ime=nosilec)
						if created:
							self.stdout.write("created new organization: %s" % (n))
						r, created = racunalnik.objects.get_or_create(
							ime=model,
							opombe=opombe,
							tip=tip,
							kraj=kraj,
							nakup=letnica,
							generacija=generacija,
							uporaba=uporaba,
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

						for org in uporabniki:
							org = org.strip()
							o, created = organizacija.objects.get_or_create(ime=org)
							if created:
								self.stdout.write("created new org: %s" % (o))
							r.organizacija.add(o)

						for org in partnerji:
							org = org.strip()
							o, created = organizacija.objects.get_or_create(ime=org)
							if created:
								self.stdout.write("created new org: %s" % (o))
							r.organizacija.add(o)

						r.save()
