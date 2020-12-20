from django.urls import path

from apps.user import views

app_name = 'user'


urlpatterns = [
    path('login/', views.user_login, name='user_login'),
]
