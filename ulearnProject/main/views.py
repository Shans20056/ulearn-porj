from django.shortcuts import render
from .models import Article

def article_list(request):
    articles = Article.objects.all()
    return render(request, 'article_list.html', {'articles': articles})

def home(request):
    return render(request, 'main/home.html', {
        'title': 'Главная страница'
    })

def about(request):
    return render(request, 'main/about.html', {
        'title': 'О нас'
    })

def contact(request):
    return render(request, 'main/contact.html', {
        'title': 'Контакты'
    })
