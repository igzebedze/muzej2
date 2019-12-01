import csv
import os

from muzej2.models import Eksponat, Primerek

with open('eksponati.csv') as csvfile:
	reader = csv.DictReader(csvfile)
	headers = next(reader, None)
	for row in reader:
		print(row)
		obj, created = Eksponat.objects.get_or_create(ime=row[0])
		print (created)
		obj.tip = ""
		obj.visina_cm = 1
		obj.dolzina_cm = 30
		obj.sirina_cm = 20
		obj.opis = "revija, ki je izhajala v sloveniji v slovenskem jeziku"
		obj.kategorija = 20
		obj.wikipedia = ""
		obj.oldcomputers = row[4]
		obj.stran = row[3]
		obj.vir = row[5]
		
		obj.save()
		break
