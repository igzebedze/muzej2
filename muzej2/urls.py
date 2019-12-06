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
from django.urls import path
from django.contrib import admin

from inventura.views import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',HomeView, name='home'),
    path('eksponat/', KategorijaList.as_view(), name='kazalo'),
	path('vhod/<int:id>/', vhod),	#  r'^vhod/([0-9]+)/'
	path('v/<int:id>/', vhod_short),	# r'^[vV]/([0-9]+)/?'
	path('izhod/<int:id>/', izhod),
	path('x/<int:id>/', izhod_short),
	path('i/<int:id>/', primerek_short),	# r'^[iI]/([0-9]+)/?'
	path('premik/', premik),
    path('izvoz/', PrimerekList.as_view(), name='izvoz'),
	path('eksponat/<int:pk>/', EksponatView.as_view(), name='eksponat-detail'),
	path('razstava/<int:pk>/', RazstavaView.as_view(), name='razstava-detail'),
#	path(r'^wiki/', include('wiki.urls')),
#	path(r'^autocomplete/', include('autocomplete_light.urls')),
]
