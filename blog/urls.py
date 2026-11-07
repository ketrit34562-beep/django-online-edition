from django.urls import path
from . import views

urlpatterns = [
    path('', views.post_list, name='post_list'),
    path('article/<int:article_id>/', views.article_detail, name='article_detail'),
    path('statistics/', views.statistics, name='statistics'),
]