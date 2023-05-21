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

from inventura.views import *
from evidenca.views import *

router = routers.DefaultRouter()
router.register(r'eksponati', HeroViewSet)
router.register(r'eksponati/<int:pk>/', HeroViewSet)
router.register(r'razstave', RazstaveViewSet)
router.register(r'razstave/<int:pk>/', RazstaveViewSet)
router.register(r'statistika', KategorijeViewSet)
router.register(r'evidenca', RacunalnikViewSet)
router.register(r'evidenca/<int:pk>/', RacunalnikViewSet)

urlpatterns = [
	path('', terminalView, name='terminal'),
    path('admin/', admin.site.urls),
    path('adminactions/', include('adminactions.urls')),
    path('home/', HomeView, name='home'),

    path('app/', appView, name='app'),
    path('app/<int:pk>/', appEksponat),
    path('app/<str:category>/', appView),
    path('app/proizvajalec/<int:pk>/', appProizvajalec),

#    path('revije/', revijeIndexView.as_view()),
    path('revije/', revijeYearsView.as_view()),
    path('revije/oprojektu/', TemplateView.as_view(template_name='inventura/revijeoprojektu.html'), name='oprojektu'), 
    path('revije/<int:pk>/js', revijaJSView),
    path('revije/<int:pk>/thumbs', revijaThumbsView),
    path('revije/<int:pk>/', revijaView.as_view()),
    path('revije/<str:tip>/', revijaYearsView),

    path('galerija/', GalerijaList.as_view(), name='galerija'),
    path('proizvajalec/', ProizvajalecList.as_view(), name='proizvajalci'),

	path('vhod/<int:id>/', vhod),	#  r'^vhod/([0-9]+)/'
	path('v/<int:id>/', vhod_short),	# r'^[vV]/([0-9]+)/?'
	path('izhod/<int:id>/', izhod),
	path('x/<int:id>/', izhod_short),
	path('i/<int:id>/', primerek_short),	# r'^[iI]/([0-9]+)/?'
	path('premik/', premik),
	path('stat/', stat),
    path('izvoz/', PrimerekList.as_view(), name='izvoz'),
    path('listki/', listki, name='listki'),

    path('eksponat/', KategorijaList.as_view(), name='kazalo'),
	path('eksponat/<int:pk>/', EksponatView.as_view(), name='eksponat-detail'),
    path('eksponat/<int:pk>/uredi/', update_infobox, name='infobox-edit'),

	path('razstava/<int:pk>/', RazstavaView.as_view(), name='razstava-detail'),
 
    path('evidenca/', RacunalnikListView.as_view(), name='racunalniki'),
    path('evidenca/geojson/', RacunalnikiGeoJsonView.as_view(), name='geojson'),
    path('evidenca/<int:pk>/', racunalnik_detail_rendered),
    path('evidenca/zemljevid/', RacunalnikiZemljevid.as_view(), name='zemljevid'), 
    path('evidenca/oprojektu/', TemplateView.as_view(template_name='evidenca/oprojektu.html'), name='oprojektu'), 
    path('evidenca/organizacije/', OrganizacijeListView.as_view(), name='organizacije'),
    path('evidenca/osebe/', OsebaListView.as_view(), name='osebe'),
    path('evidenca/osebe/<int:pk>/', OsebaView),

#	path(r'^wiki/', include('wiki.urls')),
#	path(r'^autocomplete/', include('autocomplete_light.urls')),

	path('api/', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('slides/', include('django.contrib.flatpages.urls')),
    path('search/', include('haystack.urls')),

    path('accounts/', include('django_registration.backends.activation.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/profile/', user_profile),
] 
if settings.DEBUG is True:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)