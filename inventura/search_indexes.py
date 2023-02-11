# products/search_indexes.py 
from haystack import indexes 
from inventura.models import Stran, Primerek

class RevijeIndex(indexes.ModelSearchIndex, indexes.Indexable):
    class Meta:
        model = Stran
        fields = ['ocr', 'cistopis', 'tiskovina__revija__eksponat__ime']

class PredmetiIndex(indexes.ModelSearchIndex, indexes.Indexable):
    class Meta:
        model = Primerek
        fields = ['eksponat__opis', 'eksponat__ime', 'eksponat__kategorija', 'zgodovina', 'stanje', 'eksponat__tip', 'vhodni_dokument__opis']
