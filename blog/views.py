from django.shortcuts import render, get_object_or_404, redirect
from django.db.models.functions import TruncDate
from django.db.models import Count, Q, Max
from django.core.paginator import Paginator
from django.contrib import messages
from  django.contrib.auth import login, logout, authenticate
from .models import (
    Article,
    Category,
    Author,
    EditorialReview,
    Comment,
    ArticleTag,
)
from .forms import ArticleForm, CommentForm, RegistrationForm, LoginForm
import hashlib
from django.contrib.auth.models import User as AuthUser
from django.contrib.auth.hashers import check_password
from .models import User as BlogUser, Role
from django.contrib.auth.decorators import login_required, user_passes_test

from django.contrib.auth.decorators import user_passes_test

def is_editorial_staff(user):
    if not user.is_authenticated:
        return False
    blog_user = (
        BlogUser.objects
        .select_related('role')
        .filter(username=user.username)
        .first()
    )
    return bool(
        blog_user
        and blog_user.role
        and blog_user.role.role_name in ['Администратор', 'Редактор', 'Писатель']
    )

def is_superuser_check(user):
    return user.is_authenticated and user.is_superuser


def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            blog_user = form.save()

            auth_user, _ = AuthUser.objects.get_or_create(
                username=blog_user.username,
                defaults={'email': blog_user.email}
            )
            auth_user.is_active = True
            auth_user.is_staff = False
            auth_user.is_superuser = False
            auth_user.save()

            login(request, auth_user)
            return redirect('post_list')
    else:
        form = RegistrationForm()
    return render(
        request,
        'blog/registration/register.html',
        {'form': form}
    )



def verify_password(raw_password, stored_hash):
    if not stored_hash:
        return False
    if stored_hash.startswith('pbkdf2_'):
        return check_password(raw_password, stored_hash)
    sha256_hash = hashlib.sha256(raw_password.encode('utf-8')).hexdigest()
    return sha256_hash == stored_hash


def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            # Ищем пользователя в вашей таблице USERS и проверяем хеш
            blog_user = (
                BlogUser.objects
                .select_related('role')
                .filter(username=username, is_active=True)
                .first()
            )

            if blog_user and verify_password(password, blog_user.password_hash):
                # Создаём только техническую сессию для сайта (без доступа к /admin/)
                auth_user, _ = AuthUser.objects.get_or_create(
                    username=blog_user.username,
                    defaults={'email': blog_user.email}
                )
                auth_user.is_active = True
                auth_user.is_staff = False      # <-- Закрываем доступ в системную админку /admin/
                auth_user.is_superuser = False  # <-- Все права берём только из вашей таблицы USERS
                auth_user.save()

                login(request, auth_user)

                return redirect('post_list')

            messages.error(request, 'Неверное имя пользователя или пароль.')
    else:
        form = LoginForm()
    return render(
        request,
        'blog/registration/login.html',
        {'form': form}
    )

def user_logout(request):
    logout(request)
    messages.success(request, 'Вы вышли из аккаунта.')
    return redirect('post_list')


def post_list(request):
    query = request.GET.get('q', '').strip()
    category_id = request.GET.get('category')
    tag_id = request.GET.get('tag')

    if request.user.is_superuser:
        articles = (
            Article.objects
            .exclude(category__isnull=True)
            .select_related('author', 'category')
            .prefetch_related('tags', 'image_set')
            .distinct()
        )
    else:
        articles = (
            Article.objects
            .filter(editorialreview__decision='Опубликовать')
            .exclude(category__isnull=True)
            .select_related('author', 'category')
            .prefetch_related('tags', 'image_set')
            .distinct()
        )

    if category_id:
        articles = articles.filter(category_id=category_id)
    if tag_id:
        articles = articles.filter(tags__tag_id=tag_id)
    if query:
        articles = articles.filter(
            Q(title__icontains=query) |
            Q(short_description__icontains=query)
        )

    archive_stats = articles.aggregate(
        total_articles=Count('article_id', distinct=True),
        total_authors=Count('author_id', distinct=True),
        last_published=Max('published_at')
    )

    articles = articles.order_by('-published_at')

    paginator = Paginator(articles, 6)
    page_number = request.GET.get('page')
    articles = paginator.get_page(page_number)

    categories = Category.objects.annotate(
        articles_count=Count(
            'article',
            filter=Q(article__editorialreview__decision='Опубликовать'),
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
            'archive_stats': archive_stats,
        }
    )

@user_passes_test(is_editorial_staff, login_url='login')
def article_detail(request, article_id):
    queryset = (
        Article.objects
        .filter(editorialreview__decision='Опубликовать')
        .select_related('author', 'category')
        .prefetch_related('tags', 'image_set')
        .distinct()
    )
    article = get_object_or_404(queryset, article_id=article_id)

    comment_form = CommentForm()
    editorial_review = (
        EditorialReview.objects
        .filter(article=article, decision='Опубликовать')
        .select_related('reviewer')
        .order_by('-reviewed_at')
        .first()
    )

    if request.method == 'POST':
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.article = article
            comment.status = 'На проверке'
            comment.save()
            messages.success(request, 'Комментарий отправлен на проверку.')
            return redirect('article_detail', article_id=article.article_id)

    related_articles = (
        Article.objects
        .filter(
            editorialreview__decision='Опубликовать',
            tags__in=article.tags.all()
        )
        .exclude(article_id=article.article_id)
        .distinct()
        .order_by('-published_at')[:3]
    )

    comments = (
        Comment.objects
        .filter(article=article)
        .exclude(status='На проверке')
        .select_related('user')
        .order_by('created_at')
    )

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

@user_passes_test(is_editorial_staff, login_url='login')
def statistics(request):
    published_articles = (
        Article.objects
        .filter(editorialreview__decision='Опубликовать')
        .exclude(editorialreview__decision__in=['Отклонить', 'На доработку'])
        .exclude(category__isnull=True)
        .distinct()
    )

    categories = (
        published_articles
        .values('category__category_name')
        .annotate(total=Count('article_id', distinct=True))
        .order_by('-total')
    )

    authors = (
        published_articles
        .values('author__first_name', 'author__last_name')
        .annotate(total=Count('article_id', distinct=True))
        .order_by('-total')
    )

    dates = (
        published_articles
        .annotate(day=TruncDate('published_at'))
        .values('day')
        .annotate(total=Count('article_id', distinct=True))
        .order_by('day')
    )

    statuses = (
        Article.objects
        .values('status')
        .annotate(total=Count('article_id'))
    )

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

@user_passes_test(is_editorial_staff, login_url='login')
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
            messages.success(request, 'Публикация успешно добавлена!')
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

@login_required(login_url='user_login')
def article_manage(request):
    articles = (
        Article.objects
        .select_related('author', 'category')
        .order_by('-created_at')
    )
    return render(
        request,
        'blog/post/manage.html',
        {'articles': articles}
    )

@user_passes_test(is_editorial_staff, login_url='login')
def article_edit(request, article_id):
    article = get_object_or_404(Article, article_id=article_id)
    if request.method == 'POST':
        form = ArticleForm(request.POST, instance=article)
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
            messages.success(request, 'Публикация успешно обновлена!')
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

@user_passes_test(is_editorial_staff, login_url='login')
def article_delete(request, article_id):
    article = get_object_or_404(Article, article_id=article_id)
    if request.method == 'POST':
        article.delete()
        messages.success(request, 'Публикация успешно удалена!')
        return redirect('article_manage')
    return render(
        request,
        'blog/post/delete.html',
        {'article': article}
    )


def author_list(request):
    authors = Author.objects.all().order_by('last_name', 'first_name')
    return render(
        request,
        'blog/author/list.html',
        {'authors': authors}
    )


def author_detail(request, author_id):
    author = get_object_or_404(Author, author_id=author_id)
    articles = (
        Article.objects
        .filter(
            author=author,
            editorialreview__decision='Опубликовать'
        )
        .select_related('category')
        .distinct()
        .order_by('-published_at')
    )
    return render(
        request,
        'blog/author/detail.html',
        {
            'author': author,
            'articles': articles,
        }
    )
