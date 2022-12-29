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
from django.conf.urls.static import static
from rest_framework import routers

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
	path('api/', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework'))
] 
if settings.DEBUG is True:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)