from django.shortcuts import render
from django.db.models.functions import TruncDate
from .models import Article, Category
from django.db import connection
from django.db.models import Count, Q
from django.core.paginator import Paginator


def post_list(request):
    query = request.GET.get('q', '').strip()
    category_id = request.GET.get('category')

    # Подключаем функцию для сравнения текста без учёта регистра
    connection.ensure_connection()
    connection.connection.create_function(
        'unicode_lower',
        1,
        lambda value: value.lower() if value else ''
    )

    articles = Article.objects.filter(
        status='Опубликовано'
    )
    if category_id:
        articles = articles.filter(category_id=category_id)

    if query:
        articles = articles.extra(
            where=[
                "unicode_lower(title) LIKE unicode_lower(%s)"
            ],
            params=[f'%{query}%']
        )

    articles = articles.order_by('-published_at')
    paginator = Paginator(articles, 6)
    page_number = request.GET.get('page')
    articles = paginator.get_page(page_number)

    categories = Category.objects.annotate(
        articles_count=Count(
            'article',
            filter=Q(article__status='Опубликовано')
        )
    ).order_by('-articles_count', 'category_name')

    popular_categories = categories[:6]
    other_categories = categories[6:]

    return render(
        request,
        'blog/post/list.html',
        {
            'articles': articles,
            'query': query,
            'popular_categories': popular_categories,
            'other_categories': other_categories,
            'category_id': category_id,

        }
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

