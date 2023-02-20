# products/search_indexes.py 
from haystack import indexes 
from inventura.models import Stran, Primerek
from evidenca.models import racunalnik, vir
#from whoosh.analysis import StemmingAnalyzer
#from gensim.parsing.porter import PorterStemmer
#from whoosh.fields import TEXT, ID, Schema

#stemmer = PorterStemmer(lang='sl')
#analyzer = StemmingAnalyzer(stemfn=stemmer.stem)

class RevijeIndex(indexes.ModelSearchIndex, indexes.Indexable):
    class Meta:
        model = Stran
        exclude = ['dnevnik', 'created_at', 'updated_at']
        #fields = ['ocr', 'cistopis', 'tiskovina__revija__eksponat__ime']

#    def prepare(self, obj):
#        self.prepared_data = super(RevijeIndex, self).prepare(obj)
#        self.prepared_data['text'] = self.prepared_data['text'].lower()
#        self.prepared_data['text'] = ' '.join([token.text for token in analyzer(self.prepared_data['text'])])
#        return self.prepared_data

class PredmetiIndex(indexes.ModelSearchIndex, indexes.Indexable):
    class Meta:
        model = Primerek
        exclude = ['dnevnik', 'created_at', 'updated_at']
        #fields = ['eksponat__opis', 'eksponat__ime', 'eksponat__kategorija', 'zgodovina', 'stanje', 'eksponat__tip', 'vhodni_dokument__opis']

class EvidencaIndex(indexes.ModelSearchIndex, indexes.Indexable):
    class Meta:
        model = vir
        exclude = ['dnevnik', 'created_at', 'updated_at']
        #fields = ['vsebina', 'naslov']