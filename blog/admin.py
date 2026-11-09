from django.contrib import admin
from django.contrib.auth.models import Group
from django.utils import timezone
from import_export import resources
from import_export.admin import ExportMixin
from simple_history.admin import SimpleHistoryAdmin

from .models import (
    Role,
    User,
    Author,
    Category,
    Article,
    Tag,
    ArticleTag,
    Image,
    Comment,
    EditorialReview,
)


class ImageInline(admin.TabularInline):
    model = Image
    extra = 1

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name in ['uploaded_by', 'updated_by']:
            kwargs['queryset'] = User.objects.filter(
                role__role_name='Редактор'
            )
        return super().formfield_for_foreignkey(
            db_field, request, **kwargs
        )


@admin.register(Image)
class ImageAdmin(SimpleHistoryAdmin):
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name in ['uploaded_by', 'updated_by']:
            kwargs['queryset'] = User.objects.filter(
                role__role_name='Редактор'
            )
        return super().formfield_for_foreignkey(
            db_field, request, **kwargs
        )


class ArticleResource(resources.ModelResource):
    class Meta:
        model = Article


class CategoryResource(resources.ModelResource):
    class Meta:
        model = Category


class ArticleAdmin(ExportMixin, SimpleHistoryAdmin):
    resource_class = ArticleResource
    list_display = [
        'article_id',
        'title',
        'short_description',
        'author_and_category',
        'author',
        'category',
        'status',
        'created_at',
        'published_at',
    ]
    list_display_links = ['article_id', 'title']
    search_fields = [
        'title',
        'short_description',
        'content',
        'author__first_name',
        'author__last_name',
    ]
    list_filter = ['status', 'category', 'created_at']
    date_hierarchy = 'created_at'
    readonly_fields = [
        'article_id',
        'created_at',
        'updated_at',
        'published_at',
    ]
    raw_id_fields = ['author', 'category']
    inlines = [ImageInline]

    @admin.display(description='Автор и категория')
    def author_and_category(self, obj):
        return f'{obj.author} — {obj.category}'

    @admin.display(description='Краткое описание')
    def short_description(self, obj):
        if len(obj.short_description) > 50:
            return obj.short_description[:50] + '...'
        return obj.short_description

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'updated_by':
            article_id = request.resolver_match.kwargs.get('object_id')
            if article_id:
                article = Article.objects.filter(
                    article_id=article_id
                ).select_related('author__user').first()
                if article:
                    author_user = article.author.user
                    kwargs['queryset'] = User.objects.filter(
                        user_id=author_user.user_id
                    )
                    field = super().formfield_for_foreignkey(
                        db_field, request, **kwargs
                    )
                    field.label_from_instance = lambda user: (
                        f'{article.author.first_name} {article.author.last_name}'
                    )
                    return field
        return super().formfield_for_foreignkey(
            db_field, request, **kwargs
        )


@admin.register(Author)
class AuthorAdmin(SimpleHistoryAdmin):
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name in ['created_by', 'updated_by']:
            kwargs['queryset'] = User.objects.filter(
                role__role_name='Администратор'
            )
        elif db_field.name == 'user':
            kwargs['queryset'] = User.objects.filter(
                role__role_name='Автор'
            )
        return super().formfield_for_foreignkey(
            db_field, request, **kwargs
        )


admin.site.register(Article, ArticleAdmin)
admin.site.register([Role, User])


@admin.register(Tag)
class TagAdmin(SimpleHistoryAdmin):
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name in ['created_by', 'updated_by']:
            kwargs['queryset'] = User.objects.filter(
                role__role_name='Редактор'
            )
        return super().formfield_for_foreignkey(
            db_field, request, **kwargs
        )


@admin.register(ArticleTag)
class ArticleTagAdmin(SimpleHistoryAdmin):
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'created_by':
            kwargs['queryset'] = User.objects.filter(
                role__role_name='Редактор'
            )
        return super().formfield_for_foreignkey(
            db_field, request, **kwargs
        )


class EditorialReviewAdmin(SimpleHistoryAdmin):
    list_display = [
        'review_id',
        'article',
        'reviewer',
        'decision',
        'reviewed_at',
    ]
    list_filter = ['decision', 'reviewed_at']
    search_fields = [
        'article__title',
        'review_comments',
    ]

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'article':
            kwargs['queryset'] = Article.objects.filter(
                status='Отправить на проверку'
            )
        elif db_field.name in ['reviewer', 'updated_by']:
            kwargs['queryset'] = User.objects.filter(
                role__role_name='Редактор'
            )
        return super().formfield_for_foreignkey(
            db_field, request, **kwargs
        )

    def save_model(self, request, obj, form, change):
        obj.reviewed_at = timezone.now()
        super().save_model(request, obj, form, change)
        if obj.decision == 'Опубликовать':
            obj.article.published_at = obj.reviewed_at
            obj.article.save(update_fields=['published_at'])


admin.site.register(EditorialReview, EditorialReviewAdmin)
admin.site.unregister(Group)


@admin.register(Category)
class CategoryAdmin(ExportMixin, SimpleHistoryAdmin):
    resource_class = CategoryResource

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name in ['created_by', 'updated_by']:
            kwargs['queryset'] = User.objects.filter(
                role__role_name='Редактор'
            )
        return super().formfield_for_foreignkey(
            db_field, request, **kwargs
        )


@admin.register(Comment)
class CommentAdmin(SimpleHistoryAdmin):
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'user':
            kwargs['queryset'] = User.objects.filter(
                role__role_name='Читатель'
            )
        elif db_field.name == 'updated_by':
            kwargs['queryset'] = User.objects.filter(
                role__role_name__in=['Читатель', 'Администратор']
            )
        return super().formfield_for_foreignkey(
            db_field, request, **kwargs
        )

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser or (
            request.user.is_staff and
            User.objects.filter(
                username=request.user.username,
                role__role_name='Администратор'
            ).exists()
        )


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    filter_horizontal = ['permissions']
    search_fields = ['name']
