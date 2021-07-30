from django.urls import path

from . import views


app_name = 'log'
urlpatterns = [
    path('proxy/email/', views.proxy_send_email, name='proxy_send_email'),
]
