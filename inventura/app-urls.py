from django.urls import path
from django.conf.urls.static import static
from django.views.generic import RedirectView

from inventura.views import *

urlpatterns = [
    path('', RedirectView.as_view(url='/app/', permanent=True)),
    path('app/', appView, name='app'),
    path('app/<int:pk>/', appEksponat, name='eksponat'),
    path('app/<str:category>/', appView, name='app'),
    path('app/proizvajalec/<int:pk>/', appProizvajalec, name='proizvajalec'),
] 
if settings.DEBUG is True:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)