# products/search_indexes.py 
from haystack import indexes 
from inventura.models import Stran, Primerek
from evidenca.models import racunalnik, vir

from lemmagen3 import Lemmatizer

lemmatizer = Lemmatizer('sl')

class RevijeIndex(indexes.ModelSearchIndex, indexes.Indexable):
    class Meta:
        model = Stran
        exclude = ['dnevnik', 'created_at', 'updated_at']
        #fields = ['ocr', 'cistopis', 'tiskovina__eksponat__ime']

    def prepare(self, obj):
        self.prepared_data = super(RevijeIndex, self).prepare(obj)
        tokens = self.prepared_data['text'].lower().split()
        self.prepared_data['text'] = ' '.join([lemmatizer.lemmatize(token) for token in tokens])
        return self.prepared_data

#class PredmetiIndex(indexes.ModelSearchIndex, indexes.Indexable):
#    class Meta:
#        model = Primerek
#        exclude = ['dnevnik', 'created_at', 'updated_at']
        #fields = ['eksponat__opis', 'eksponat__ime', 'eksponat__kategorija', 'zgodovina', 'stanje', 'eksponat__tip', 'vhodni_dokument__opis']

#    def prepare(self, obj):
#        self.prepared_data = super(PredmetiIndex, self).prepare(obj)
#        tokens = self.prepared_data['text'].lower().split()
#        self.prepared_data['text'] = ' '.join([lemmatizer.lemmatize(token) for token in tokens])
#        return self.prepared_data

class EvidencaIndex(indexes.ModelSearchIndex, indexes.Indexable):
    class Meta:
        model = vir
        exclude = ['dnevnik', 'created_at', 'updated_at']
        #fields = ['vsebina', 'naslov']

    def prepare(self, obj):
        self.prepared_data = super(EvidencaIndex, self).prepare(obj)
        tokens = self.prepared_data['text'].lower().split()
        self.prepared_data['text'] = ' '.join([lemmatizer.lemmatize(token) for token in tokens])
        return self.prepared_data
