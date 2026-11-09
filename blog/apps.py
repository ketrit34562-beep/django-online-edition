from django.apps import AppConfig
from django.db.backends.signals import connection_created


def activate_sqlite_unicode_lower(sender, connection, **kwargs):
    if connection.vendor == 'sqlite':
        connection.connection.create_function(
            'LOWER',
            1,
            lambda value: value.lower() if value is not None else None
        )


class BlogConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'blog'

    def ready(self):
        connection_created.connect(activate_sqlite_unicode_lower)
