from django.urls import path

from . import views


app_name="coa"
urlpatterns = [
    path('upload/', views.upload, name="upload"),
    path('proxy/parser/', views.proxy_parser, name='proxy_parser'),
    path('proxy/build/', views.proxy_build, name='proxy_build'),
]
