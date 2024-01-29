from inventura.models import Tiskovina, Primerek, Eksponat

for t in Tiskovina.objects.all():
    e = t.eksponat
    if not t.leto or t.leto is None:
        continue
    if not t.mesec or t.mesec is None:
        continue
    s = "%d-%d" % (t.leto, t.mesec)
    try:
        p = Primerek.objects.get(eksponat=e, serijska_st=s)
    except:
        pass
    else:
        print("%s :: %s %s"% (t, p, p.serijska_st))
        t.primerek = p
        t.save()