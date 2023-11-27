from django.urls import path
from theme.views import HomePageView

urlpatterns = [
    path("", HomePageView.as_view(), name="themetest"),
]