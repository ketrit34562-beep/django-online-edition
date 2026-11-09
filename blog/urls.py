from django.urls import path
from . import views

urlpatterns = [
    path('', views.post_list, name='post_list'),
    path('logout/', views.user_logout, name='logout'),
    path('login/', views.user_login, name='login'),
    path('register/', views.register, name='register'),
    path('article/<int:article_id>/', views.article_detail, name='article_detail'),
    path('article/create/', views.article_create, name='article_create'),
    path('articles/manage/', views.article_manage, name='article_manage'),
    path('article/<int:article_id>/edit/', views.article_edit, name='article_edit'),
    path('article/<int:article_id>/delete/', views.article_delete, name='article_delete'),
    path('statistics/', views.statistics, name='statistics'),
    path('authors/', views.author_list, name='author_list'),
    path('author/<int:author_id>/', views.author_detail, name='author_detail'),
]