from django.contrib import admin
from django.urls import path, include
from perpustakaan import views

urlpatterns = [
    path('', include('perpustakaan.urls')),
]