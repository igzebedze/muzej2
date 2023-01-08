"""muzej2 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/dev/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path, include
from django.contrib import admin
from django.conf.urls.static import static
from rest_framework import routers
from django.views.generic import TemplateView

from evidenca.views import *

router = routers.DefaultRouter()
router.register(r'', RacunalnikViewSet)
router.register(r'/<int:pk>/', RacunalnikViewSet)

urlpatterns = [
    path('', RacunalnikListView.as_view(), name='racunalniki'),
    path('geojson/', RacunalnikiGeoJsonView.as_view(), name='geojson'),
    path('<int:pk>/', racunalnik_detail_rendered),
    path('zemljevid/', RacunalnikiZemljevid.as_view(), name='zemljevid'), 
    path('oprojektu/', TemplateView.as_view(template_name='evidenca/oprojektu.html'), name='oprojektu'), 
    path('organizacije/', OrganizacijeListView.as_view(), name='organizacije'),
    path('osebe/', OsebaListView.as_view(), name='osebe'),
    path('osebe/<int:pk>/', OsebaView),

] 
if settings.DEBUG is True:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)