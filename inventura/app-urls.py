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
from django.conf.urls.static import static
from django.views.generic import RedirectView

from inventura.views import *

urlpatterns = [
    path('^$', RedirectView.as_view(url='/app/', permanent=True)),
    path('app/', appView, name='app'),
    path('app/<int:pk>/', appEksponat, name='eksponat'),
    path('app/<str:category>/', appView, name='app'),
    path('app/proizvajalec/<int:pk>/', appProizvajalec, name='proizvajalec'),
] 
if settings.DEBUG is True:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)