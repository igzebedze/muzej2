from django.core.management.base import BaseCommand, CommandError
import re
from inventura.models import Tiskovina, Stran
import pprint

class Command(BaseCommand):
	help = 'rebuild metadata for magazine scans'
	def handle(self, *args, **options):
		pp = pprint.PrettyPrinter(indent=4)
		
		k = re.compile(r'\bvsebina\b|\bkazalo\b|\bcontents\b', flags=re.I | re.X)
		for t in Tiskovina.objects.all():
			first = t.stran_set.order_by('stevilka').first()
			for s in t.stran_set.all():
				wordcount = len(s.ocr.split())
				if s.stevilka == first.stevilka: 
					vrsta = 'naslovnica'
				elif k.match(s.ocr) and int(s.stevilka) < 5:
					vrsta = 'kazalo'
				elif wordcount < 100:
					vrsta = 'oglas'
				else:
					vrsta = 'vsebina'
						
				s.vrsta = vrsta
				s.stevilo_besed = wordcount
				s.save()

				print("%s %i %s %i" % (t, s.stevilka, s.vrsta, s.stevilo_besed))
