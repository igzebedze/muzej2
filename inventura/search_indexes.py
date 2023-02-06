# products/search_indexes.py 
from haystack import indexes 
from inventura.models import Eksponat 

class ProductIndex(indexes.SearchIndex, indexes.Indexable): 
    text = indexes.CharField(document=True, use_template=True) 
    id = indexes.IntegerField(model_attr='id') 
    ime = indexes.CharField(model_attr="ime")
    opis = indexes.CharField(model_attr="opis") 
    
    class Meta: 
      model = Eksponat 
      fields = ["text", "id", "ime", "opis"] 
      
    def get_model(self):
      return Eksponat 
      
    def index_queryset(self, using=None): 
      """Used when the entire index for model is updated.""" 
      return self.get_model().objects.all()
