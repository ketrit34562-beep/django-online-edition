from django.core.management.base import BaseCommand
from faker import Faker
from blog.models import Tag, User


class Command(BaseCommand):
    help = 'Наполнение таблицы тегов случайными данными через Faker'

    def handle(self, *args, **kwargs):
        fake = Faker('ru_RU')
        admin_user = User.objects.first()

        if not admin_user:
            self.stdout.write(
                self.style.ERROR('Ошибка: в базе данных нет ни одного пользователя для поля created_by.')
            )
            return

        created_count = 0
        for _ in range(15):
            word = fake.unique.word().capitalize()
            _, created = Tag.objects.get_or_create(
                tag_name=word,
                defaults={'created_by': admin_user}
            )
            if created:
                created_count += 1

        self.stdout.write(
            self.style.SUCCESS(f'Успешно добавлено новых тегов: {created_count}')
        )
