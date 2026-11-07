from django.db import models
from simple_history.models import HistoricalRecords



class Role(models.Model):
    role_id = models.AutoField(
        primary_key=True,
        verbose_name='Идентификатор роли'
    )
    role_name = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='Название роли'
    )
    description = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name='Описание роли'
    )

    class Meta:
        db_table = 'ROLES'
        verbose_name = 'Роль'
        verbose_name_plural = 'Роли'

    def __str__(self):
        return self.role_name



class User(models.Model):
    user_id = models.AutoField(
        primary_key=True,
        verbose_name='Идентификатор пользователя'
    )
    role = models.ForeignKey(
        Role,
        on_delete=models.PROTECT,
        db_column='role_id',
        verbose_name='Роль'
    )
    username = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='Имя пользователя'
    )
    email = models.CharField(
        max_length=255,
        unique=True,
        verbose_name='Электронная почта'
    )
    password_hash = models.CharField(
        max_length=255,
        verbose_name='Хеш пароля'
    )
    registration_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата регистрации'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Активен'
    )
    updated_at = models.DateTimeField(
        null=True,
        blank=True,
        auto_now=True,
        verbose_name='Дата изменения'
    )
    updated_by = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column='updated_by',
        related_name='updated_users',
        verbose_name='Изменил'
    )

    class Meta:
        db_table = 'USERS'
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username



class Author(models.Model):
    author_id = models.AutoField(
        primary_key=True,
        verbose_name='Идентификатор автора'
    )
    user = models.OneToOneField(
        User,
        on_delete=models.PROTECT,
        db_column='user_id',
        verbose_name='Пользователь'
    )
    first_name = models.CharField(
        max_length=100,
        verbose_name='Имя'
    )
    last_name = models.CharField(
        max_length=100,
        verbose_name='Фамилия'
    )
    biography = models.TextField(
        null=True,
        blank=True,
        verbose_name='Биография'
    )
    photo_url = models.CharField(
        max_length=500,
        null=True,
        blank=True,
        verbose_name='Ссылка на фотографию'
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        db_column='created_by',
        related_name='created_authors',
        verbose_name='Создал'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )
    updated_at = models.DateTimeField(
        null=True,
        blank=True,
        auto_now=True,
        verbose_name='Дата изменения'
    )
    updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        db_column='updated_by',
        null=True,
        blank=True,
        related_name='updated_authors',
        verbose_name='Изменил'
    )

    class Meta:
        db_table = 'AUTHORS'
        verbose_name = 'Автор'
        verbose_name_plural = 'Авторы'

    def __str__(self):
        return f'{self.first_name} {self.last_name}'



class Category(models.Model):
    category_id = models.AutoField(
        primary_key=True,
        verbose_name='Идентификатор категории'
    )
    category_name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='Название категории'
    )
    description = models.CharField(
        max_length=500,
        null=True,
        blank=True,
        verbose_name='Описание категории'
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        db_column='created_by',
        related_name='created_categories',
        verbose_name='Создал'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )
    updated_at = models.DateTimeField(
        null=True,
        blank=True,
        auto_now=True,
        verbose_name='Дата изменения'
    )
    updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        db_column='updated_by',
        null=True,
        blank=True,
        related_name='updated_categories',
        verbose_name='Изменил'
    )

    history = HistoricalRecords()

    class Meta:
        db_table = 'CATEGORIES'
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.category_name


class Article(models.Model):
    article_id = models.AutoField(
        primary_key=True,
        verbose_name='Идентификатор публикации'
    )
    author = models.ForeignKey(
        Author,
        on_delete=models.PROTECT,
        db_column='author_id',
        verbose_name='Автор'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        db_column='category_id',
        verbose_name='Категория'
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        db_column='created_by',
        related_name='created_articles',
        verbose_name='Создал'
    )
    title = models.CharField(
        max_length=255,
        verbose_name='Заголовок'
    )
    short_description = models.CharField(
        max_length=500,
        verbose_name='Краткое описание'
    )
    content = models.TextField(
        verbose_name='Содержание'
    )
    status = models.CharField(
        max_length=30,
        default='Черновик',
        verbose_name='Статус'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )
    submitted_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Дата отправки на проверку'
    )
    published_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Дата публикации'
    )
    updated_at = models.DateTimeField(
        null=True,
        blank=True,
        auto_now=True,
        verbose_name='Дата изменения'
    )
    updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        db_column='updated_by',
        null=True,
        blank=True,
        related_name='updated_articles',
        verbose_name='Изменил'
    )
    tags = models.ManyToManyField(
        'Tag',
        through='ArticleTag',
        related_name='articles',
        verbose_name='Теги'
    )

    history = HistoricalRecords()

    class Meta:
        db_table = 'ARTICLES'
        verbose_name = 'Публикация'
        verbose_name_plural = 'Публикации'
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class Tag(models.Model):
    tag_id = models.AutoField(
        primary_key=True,
        verbose_name='Идентификатор тега'
    )
    tag_name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='Название тега'
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        db_column='created_by',
        related_name='created_tags',
        verbose_name='Создал'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )
    updated_at = models.DateTimeField(
        null=True,
        blank=True,
        auto_now=True,
        verbose_name='Дата изменения'
    )
    updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        db_column='updated_by',
        null=True,
        blank=True,
        related_name='updated_tags',
        verbose_name='Изменил'
    )

    class Meta:
        db_table = 'TAGS'
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.tag_name


class ArticleTag(models.Model):
    article = models.ForeignKey(
        Article,
        on_delete=models.CASCADE,
        db_column='article_id',
        verbose_name='Публикация'
    )
    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE,
        db_column='tag_id',
        verbose_name='Тег'
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        db_column='created_by',
        related_name='created_article_tags',
        verbose_name='Создал'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )

    class Meta:
        db_table = 'ARTICLE_TAGS'
        verbose_name = 'Тег публикации'
        verbose_name_plural = 'Теги публикаций'
        constraints = [
            models.UniqueConstraint(
                fields=['article', 'tag'],
                name='unique_article_tag'
            )
        ]

    def __str__(self):
        return f'{self.article.title} — {self.tag.tag_name}'


class Image(models.Model):
    image_id = models.AutoField(
        primary_key=True,
        verbose_name='Идентификатор изображения'
    )
    article = models.ForeignKey(
        Article,
        on_delete=models.CASCADE,
        db_column='article_id',
        verbose_name='Публикация'
    )
    file_name = models.CharField(
        max_length=255,
        verbose_name='Имя файла'
    )
    file_path = models.CharField(
        max_length=500,
        verbose_name='Путь к файлу'
    )
    image_file = models.ImageField(
        upload_to='images/',
        null=True,
        blank=True,
        verbose_name='Файл изображения'
    )
    file_format = models.CharField(
        max_length=20,
        verbose_name='Формат файла'
    )
    caption = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name='Подпись'
    )
    alt_text = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name='Альтернативный текст'
    )
    uploaded_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        db_column='uploaded_by',
        related_name='uploaded_images',
        verbose_name='Загрузил'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )
    updated_at = models.DateTimeField(
        null=True,
        blank=True,
        auto_now=True,
        verbose_name='Дата изменения'
    )
    updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        db_column='updated_by',
        null=True,
        blank=True,
        related_name='updated_images',
        verbose_name='Изменил'
    )

    class Meta:
        db_table = 'IMAGES'
        verbose_name = 'Изображение'
        verbose_name_plural = 'Изображения'

    def __str__(self):
        return self.file_name



class Comment(models.Model):
    comment_id = models.AutoField(
        primary_key=True,
        verbose_name='Идентификатор комментария'
    )
    article = models.ForeignKey(
        Article,
        on_delete=models.CASCADE,
        db_column='article_id',
        verbose_name='Публикация'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        db_column='user_id',
        verbose_name='Пользователь'
    )
    comment_text = models.TextField(
        verbose_name='Текст комментария'
    )
    status = models.CharField(
        max_length=30,
        default='На проверке',
        verbose_name='Статус'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )
    updated_at = models.DateTimeField(
        null=True,
        blank=True,
        auto_now=True,
        verbose_name='Дата изменения'
    )
    updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        db_column='updated_by',
        null=True,
        blank=True,
        related_name='updated_comments',
        verbose_name='Изменил'
    )

    history = HistoricalRecords()

    class Meta:
        db_table = 'COMMENTS'
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ['-created_at']

    def __str__(self):
        return f'Комментарий к публикации №{self.article.article_id}'


class EditorialReview(models.Model):
    DECISION_CHOICES = [
        ('Одобрено', 'Одобрено'),
        ('На доработку', 'На доработку'),
        ('Отклонено', 'Отклонено'),
    ]

    review_id = models.AutoField(
        primary_key=True,
        verbose_name='Идентификатор проверки'
    )
    article = models.ForeignKey(
        Article,
        on_delete=models.CASCADE,
        db_column='article_id',
        verbose_name='Публикация'
    )
    reviewer = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        db_column='reviewer_id',
        related_name='editorial_reviews',
        verbose_name='Редактор'
    )
    decision = models.CharField(
        max_length=30,
        choices=DECISION_CHOICES,
        verbose_name='Решение'
    )
    review_comments = models.TextField(
        null=True,
        blank=True,
        verbose_name='Комментарии редактора'
    )
    reviewed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Дата проверки'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )
    updated_at = models.DateTimeField(
        null=True,
        blank=True,
        auto_now=True,
        verbose_name='Дата изменения'
    )
    updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        db_column='updated_by',
        null=True,
        blank=True,
        related_name='updated_editorial_reviews',
        verbose_name='Изменил'
    )

    class Meta:
        db_table = 'EDITORIAL_REVIEWS'
        verbose_name = 'Редакционная проверка'
        verbose_name_plural = 'Редакционные проверки'
        ordering = ['-created_at']

    def __str__(self):
        return f'Проверка публикации №{self.article.article_id}'
