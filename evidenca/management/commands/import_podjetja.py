#firma	naslov
#AERO	Kocenova ulica 4, Celje

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
	help = 'imports addresses of companies'

	def add_arguments(self, parser):
		parser.add_argument('file', nargs='+', type=str)

	def handle(self, *args, **options):
		pp = pprint.PrettyPrinter(indent=4)
		
		with open(options['file'][0]) as csvfile:
			reader = csv.DictReader(csvfile)
			#headers = next(reader, None)
			for row in reader:
				ime = row['firma']
				naslov = row['naslov']
				lat = row['Latitude']
				lon = row['Longitude']

				org = organizacija.objects.get(ime=ime)
				org.naslov=naslov
				org.latlong="(%s,%s)" % (lat,lon)
				org.save()


