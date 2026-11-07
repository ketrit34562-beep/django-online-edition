from django.shortcuts import render
from django.db.models import Count
from django.db.models.functions import TruncDate
from .models import Article


def post_list(request):
    articles = Article.objects.filter(status='Опубликовано').order_by('-published_at')

    return render(
        request,
        'blog/post/list.html',
        {'articles': articles}
    )

def article_detail(request, article_id):
    article = Article.objects.get(
        article_id=article_id,
        status='Опубликовано'
    )

    return render(
        request,
        'blog/post/detail.html',
        {'article': article}
    )
def statistics(request):
    # Количество публикаций по категориям
    categories = Article.objects.values(
        'category__category_name'
    ).annotate(total=Count('article_id'))

    # Количество публикаций по статусам
    statuses = Article.objects.values(
        'status'
    ).annotate(total=Count('article_id'))

    # Количество публикаций по авторам
    authors = Article.objects.values(
        'author__first_name',
        'author__last_name'
    ).annotate(total=Count('article_id')).order_by('-total')

    # Динамика создания публикаций по датам
    dates = Article.objects.annotate(
        day=TruncDate('created_at')
    ).values('day').annotate(
        total=Count('article_id')
    ).order_by('day')

    context = {
        'categories': list(categories),
        'statuses': list(statuses),
        'authors': list(authors),
        'dates': list(dates),
    }

    return render(request, 'blog/statistics.html', context)