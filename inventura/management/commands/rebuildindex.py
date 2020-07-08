from django.core.management.base import BaseCommand, CommandError
import csv
import os
import sys
from django.utils import timezone
from inventura.models import Eksponat, Primerek, Iskalnik
import pprint

class Command(BaseCommand):
	help = 'rebuild search index'

#	def add_arguments(self, parser):
#		parser.add_argument('file', nargs='+', type=str)

	def handle(self, *args, **options):
		pp = pprint.PrettyPrinter(indent=4)

		# flush iskalnik
		Iskalnik.objects.all().delete()

		# go through all primerek and copy fields to iskalnik
		for p in Primerek.objects.all():
			fields = (p.serijska_st, p.stanje, p.zgodovina, p.eksponat.ime, p.eksponat.tip, p.eksponat.opis)
			vsebina = ' '.join(filter(None, fields))
			i = Iskalnik(vsebina=vsebina)
			i.save()
			p.iskalnik = i
			p.save()

# 			queryset = queryset.filter(Q(eksponat__ime__search=kveri) | Q(eksponat__tip__search=kveri) | Q(eksponat__opis__search=kveri) | Q(serijska_st__search=kveri)  | Q(stanje__search=kveri) | Q(zgodovina__search=kveri))