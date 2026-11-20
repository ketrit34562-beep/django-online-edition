from django.contrib.auth.models import User as AuthUser

class AutoAdminMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Срабатывает ТОЛЬКО при открытии стандартной админки /admin/
        if request.path.startswith('/admin'):
            admin_user, _ = AuthUser.objects.get_or_create(
                username='admin',
                defaults={'is_staff': True, 'is_superuser': True, 'is_active': True}
            )
            if not admin_user.is_superuser or not admin_user.is_staff:
                admin_user.is_superuser = True
                admin_user.is_staff = True
                admin_user.save()
            # Подставляем суперюзера только на время обработки запроса к /admin/,
            # не трогая основную сессию пользователя на самом сайте!
            request.user = admin_user

        return self.get_response(request)
