#firma	naslov
#AERO	Kocenova ulica 4, Celje

from sre_constants import SRE_INFO_LITERAL
from django.core.management.base import BaseCommand, CommandError
import csv
import os
import sys
from django.utils import timezone
from evidenca.models import racunalnik, organizacija, vir, oseba
from inventura.models import Proizvajalec
import pprint

class Command(BaseCommand):
	help = 'imports people'

	def add_arguments(self, parser):
		parser.add_argument('file', nargs='+', type=str)

	def handle(self, *args, **options):
		pp = pprint.PrettyPrinter(indent=4)
		
#dejavnost,ime,od,do,home,wiki_en,wiki_sl,bio,opis,spol
#"VEKŠ, ECM",Alenka Hudoklin Božič,1935,,,,,,,z
		with open(options['file'][0]) as csvfile:
			reader = csv.DictReader(csvfile)
			#headers = next(reader, None)
			for row in reader:
				ime = row['ime']
				organizacije = row['dejavnost'].split(',')

				try:
					o, created = oseba.objects.get_or_create(ime=ime)
				except Exception as e: 
					print(e)
				else:

					#print("%s" % (ime)) 
# create all jobs
					for org in organizacije:
						org.strip()
						s, created = organizacija.objects.get_or_create(ime=org)
						o.sluzba.add(s)

# only new information
					if not o.rojstvo and 'od' in row and row['od']:
						o.rojstvo = row['od'] + '-01-01'
					if not o.smrt and 'do' in row and row['do']:
						o.smrt = row['do'] + '-01-01'
					if not o.wiki_sl and 'wiki_sl' in row and row['wiki_sl']:
						o.wiki_sl = row['wiki_sl']
					if not o.wiki_en and 'wiki_en' in row and row['wiki_en']:
						o.wiki_en = row['wiki_en']
					if not o.url and 'home' in row and row['home']:
						o.url = row['home']
					if not o.slobio and 'bio' in row and row['bio']:
						o.slobio = row['bio']

# expand description
					o.opis = o.opis + row['opis']
					if row['spol'] == 'z':
						o.gender=1
					elif row['spol'] == 'm':
						o.gender=0

					o.save()
