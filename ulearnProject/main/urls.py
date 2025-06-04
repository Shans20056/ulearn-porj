from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'), 
    path('statistics/<slug:slug>/', views.article_direct, name='article_direct'), 
]
