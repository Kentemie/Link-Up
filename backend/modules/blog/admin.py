from django.contrib import admin

from mptt.admin import DraggableMPTTAdmin

from .models import Category, Article, Comment, Rating


@admin.register(Category)
class CategoryAdmin(DraggableMPTTAdmin):

    list_display = ('tree_actions', 'indented_title', 'id', 'title', 'slug')
    list_display_links = ('title', 'slug')
    prepopulated_fields = {'slug': ('title',)}

    fieldsets = (
        ('Basic information', {'fields': ('title', 'slug', 'parent')}),
        ('Description', {'fields': ('description',)})
    )


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ["id", "title", "author", "category", "status"]
    list_filter = ["created_at"]
    prepopulated_fields = {"slug": ("title",)}


@admin.register(Comment)
class CommentAdmin(DraggableMPTTAdmin):
    list_display = ('tree_actions', 'indented_title', 'article', 'author', 'created_at', 'status')
    mptt_level_indent = 2
    list_display_links = ('article',)
    list_filter = ('created_at', 'updated_at', 'author')
    list_editable = ('status',)


@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ["id", "article", "user", "value", "created_at", "ip_address"]
    list_filter = ["created_at"]