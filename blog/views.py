from django.shortcuts import render, get_object_or_404, redirect
from django.db.models.functions import TruncDate
from django.db import connection
from django.db.models import Count, Q
from django.core.paginator import Paginator
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required

from .models import (
    Article,
    Category,
    Author,
    EditorialReview,
    User,
    Comment,
    ArticleTag,
)
from .forms import ArticleForm, CommentForm, RegistrationForm, LoginForm

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)

        if form.is_valid():
            user = form.save()
            login(request, user)

            messages.success(
                request,
                'Регистрация прошла успешно!'
            )

            return redirect('post_list')
    else:
        form = RegistrationForm()

    return render(
        request,
        'blog/registration/register.html',
        {'form': form}
    )

def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            from django.contrib.auth import authenticate

            user = authenticate(
                request,
                username=username,
                password=password
            )

            if user is not None:
                login(request, user)

                messages.success(
                    request,
                    'Вы успешно вошли в систему!'
                )

                return redirect('post_list')

            messages.error(
                request,
                'Неверное имя пользователя или пароль.'
            )
    else:
        form = LoginForm()

    return render(
        request,
        'blog/registration/login.html',
        {'form': form}
    )

def user_logout(request):
    logout(request)

    messages.success(
        request,
        'Вы вышли из аккаунта.'
    )

    return redirect('post_list')

def post_list(request):
    query = request.GET.get('q', '').strip()
    category_id = request.GET.get('category')
    tag_id = request.GET.get('tag')

    # Подключаем функцию для сравнения текста без учёта регистра
    connection.ensure_connection()
    connection.connection.create_function(
        'unicode_lower',
        1,
        lambda value: value.lower() if value else ''
    )

    articles = Article.objects.filter(
        editorialreview__decision='Опубликовать'
    ).distinct()

    if category_id:
        articles = articles.filter(category_id=category_id)

    if tag_id:
        articles = articles.filter(tags__tag_id=tag_id)

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
            filter=Q(
                article__editorialreview__decision='Опубликовать'
            ),
            distinct=True
        )
    ).order_by('-articles_count', 'category_name')

    popular_categories = categories[:5]
    other_categories = categories[5:]

    return render(
        request,
        'blog/post/list.html',
        {
            'articles': articles,
            'query': query,
            'popular_categories': popular_categories,
            'other_categories': other_categories,
            'category_id': category_id,
            'tag_id': tag_id,
        }
    )


def article_detail(request, article_id):
    article = get_object_or_404(
        Article,
        article_id=article_id,
        editorialreview__decision='Опубликовать'
    )

    comment_form = CommentForm()
    editorial_review = EditorialReview.objects.filter(
        article=article,
        decision='Опубликовать'
    ).order_by('-reviewed_at').first()

    if request.method == 'POST':
        comment_form = CommentForm(request.POST)

        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.article = article
            comment.status = 'На проверке'
            comment.save()

            messages.success(
                request,
                'Комментарий отправлен на проверку.'
            )

            return redirect(
                'article_detail',
                article_id=article.article_id
            )

    related_articles = Article.objects.filter(
        editorialreview__decision='Опубликовать',
        tags__in=article.tags.all()
    ).exclude(
        article_id=article.article_id
    ).distinct().order_by(
        '-editorialreview__reviewed_at'
    )[:3]

    comments = Comment.objects.filter(
        article=article
    ).exclude(
        status='На проверке'
    ).order_by('created_at')

    return render(
        request,
        'blog/post/detail.html',
        {
            'article': article,
            'related_articles': related_articles,
            'comments': comments,
            'comment_form': comment_form,
            'editorial_review': editorial_review,
        }
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

    return render(
        request,
        'blog/statistics.html',
        context
    )


def article_create(request):

    if request.method == 'POST':
        form = ArticleForm(request.POST)

        if form.is_valid():

            article = form.save(commit=False)
            article.save()

            for tag in form.cleaned_data['tags']:
                ArticleTag.objects.create(
                    article=article,
                    tag=tag,
                    created_by=article.author.user
                )
            messages.success(
                request,
                'Публикация успешно добавлена!'
            )

            return redirect('article_manage')
    else:
        form = ArticleForm()

    return render(
        request,
        'blog/post/forms.html',
        {
            'form': form,
            'title': 'Добавление публикации',
        }
    )


def article_manage(request):
    articles = Article.objects.select_related(
        'author',
        'category'
    ).order_by('-created_at')

    return render(
        request,
        'blog/post/manage.html',
        {'articles': articles}
    )


def article_edit(request, article_id):
    article = get_object_or_404(
        Article,
        article_id=article_id
    )

    if request.method == 'POST':
        form = ArticleForm(
            request.POST,
            instance=article
        )

        if form.is_valid():
            article = form.save(commit=False)
            article.save()

            ArticleTag.objects.filter(article=article).delete()

            for tag in form.cleaned_data['tags']:
                ArticleTag.objects.create(
                    article=article,
                    tag=tag,
                    created_by=article.author.user
                )

            messages.success(
                request,
                'Публикация успешно обновлена!'
            )

            return redirect('article_manage')
    else:
        form = ArticleForm(instance=article)

    return render(
        request,
        'blog/post/forms.html',
        {
            'form': form,
            'title': 'Редактирование публикации',
        }
    )


def article_delete(request, article_id):
    article = get_object_or_404(
        Article,
        article_id=article_id
    )

    if request.method == 'POST':
        article.delete()

        messages.success(
            request,
            'Публикация успешно удалена!'
        )

        return redirect('article_manage')

    return render(
        request,
        'blog/post/delete.html',
        {'article': article}
    )


def author_list(request):
    authors = Author.objects.all().order_by(
        'last_name',
        'first_name'
    )

    return render(
        request,
        'blog/author/list.html',
        {'authors': authors}
    )


def author_detail(request, author_id):
    author = get_object_or_404(
        Author,
        author_id=author_id
    )

    articles = Article.objects.filter(
        author=author,
        editorialreview__decision='Опубликовать'
    ).distinct().order_by(
        '-editorialreview__reviewed_at'
    )

    return render(
        request,
        'blog/author/detail.html',
        {
            'author': author,
            'articles': articles,
        }
    )
