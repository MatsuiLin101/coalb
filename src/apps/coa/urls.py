from django.urls import path

from . import views


app_name="coa"
urlpatterns = [
    path('upload/', views.upload, name="upload")
]
