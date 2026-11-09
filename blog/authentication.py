import hashlib
from django.contrib.auth.hashers import check_password
from django.contrib.auth.backends import BaseBackend

from .models import User


class CustomUserBackend(BaseBackend):

    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None:
            username = kwargs.get('email')

        if not username or not password:
            return None

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return None

        password_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()

        if user.is_active and (
                user.password_hash == password_hash
                or check_password(password, user.password_hash)
        ):
            return user

        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id, is_active=True)
        except User.DoesNotExist:
            return None