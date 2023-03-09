from django.urls import path
from django.conf.urls.static import static
from django.views.generic import TemplateView

from inventura.views import *

urlpatterns = [
    path('', revijeYearsView.as_view()),
    path('<str:tip>/', revijaYearsView),
    path('oprojektu/', TemplateView.as_view(template_name='inventura/revijeoprojektu.html'), name='oprojektu'), 
    path('revije/<int:pk>/js', revijaJSView),
    path('revije/<int:pk>/thumbs', revijaThumbsView),
    path('revije/<int:pk>/', revijaView.as_view()),
] 
if settings.DEBUG is True:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)