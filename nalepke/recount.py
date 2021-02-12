# move PDFs to numbers above #11391 by exchanging IDs

from inventura.models import Primerek

max = 11392
for p in Primerek.objects.filter(eksponat__ime__icontains="pdf", eksponat__kategorija__id__exact=20):
	next = Primerek.objects.get(inventarna_st=max)
	
	next.inventarna_st = p.inventarna_st
	p.inventarna_st = max
	next.save()
	p.save()
	
	max = max + 1
	break