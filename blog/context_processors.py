from .models import User as BlogUser

def user_role_context(request):
    can_manage = False

    if request.user.is_authenticated:
        blog_user = (
            BlogUser.objects
            .select_related('role')
            .filter(username=request.user.username)
            .first()
        )
        if blog_user and blog_user.role:
            # Доступ только для Администратора, Редактора и Писателя
            if blog_user.role.role_name in ['Администратор', 'Редактор', 'Автор']:
                can_manage = True

    return {
        'can_manage_content': can_manage,
    }