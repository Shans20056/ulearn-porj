from django.urls import path
from . import views

urlpatterns = [
    path('', views.article_list, name='article_list'),
    path('home/', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
]