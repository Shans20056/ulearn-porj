from django.shortcuts import render
from .models import Article

def article_direct(request, slug):
    article = Article.objects.get(slug=slug)
    return render(request, 'main/article_direct.html', {'article': article})


def article_list(request):
    articles = Article.objects.all()
    return render(request, 'article_list.html', {'articles': articles})


def home(request):
    return render(request, 'main/home.html', {
        'title': 'Главная страница'
    })



