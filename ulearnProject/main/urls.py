from django.urls import path
from . import views

urlpatterns = [
    path('', views.article_list, name='home'), 
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('statistics/<slug:slug>/', views.article_direct, name='article_direct'), 
]
