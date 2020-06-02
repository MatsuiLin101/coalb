from django.urls import path

from apps.users import views

app_name = 'users'


urlpatterns = [
    path('login/', views.user_login, name='user_login'),
]
