from django.contrib.auth.models import Group
from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from import_export import resources
from import_export.admin import ExportMixin
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
    ]
    raw_id_fields = ['author', 'category', 'created_by', 'updated_by']
    inlines = [ImageInline]


    @admin.display(description='Автор и категория')
    def author_and_category(self, obj):
        return f'{obj.author} — {obj.category}'

    def short_description(self, obj):
        return obj.short_description[:50] + '...' if len(obj.short_description) > 50 else obj.short_description

    short_description.short_description = 'Краткое описание'



admin.site.register(Article, ArticleAdmin)

admin.site.register([
    Role,
    User,
    Author,
    Tag,
    ArticleTag,
    Image,
    EditorialReview,
])

admin.site.unregister(Group)

@admin.register(Category)
class CategoryAdmin(ExportMixin, SimpleHistoryAdmin):
    resource_class = CategoryResource

@admin.register(Comment)
class CommentAdmin(SimpleHistoryAdmin):
    pass

@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    filter_horizontal = ['permissions']
    search_fields = ['name']