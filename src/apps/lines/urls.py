from django.urls import path
from .views import home, callback


urlpatterns = [
    path('', home),
    path('callback/', callback),
]
