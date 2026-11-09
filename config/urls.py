"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import get_user_model


# Функция для автоматического входа без пароля при локальной разработке
def auto_login_admin(request):
    if not request.user.is_authenticated:
        User = get_user_model()
        # Сначала пытаемся найти вашего пользователя admin_editor
        admin_user = User.objects.filter(username='admin_editor').first()

        # Если такого нет, берем любого администратора из базы данных
        if not admin_user:
            admin_user = User.objects.filter(is_superuser=True).first() or User.objects.filter(is_staff=True).first()

        if admin_user:
            request.user = admin_user
    return True


# Отключаем защитную форму логина Django только в режиме отладки (DEBUG = True)
if settings.DEBUG:
    admin.site.has_permission = auto_login_admin

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('blog.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
