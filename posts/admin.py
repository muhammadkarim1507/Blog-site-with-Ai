from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Post, Like, Comment


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'colored_badge', 'post_count', 'created_at']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}

    def colored_badge(self, obj):
        return format_html(
            '<span style="background:{}; color:#fff; padding:3px 10px; border-radius:20px;">{}</span>',
            obj.color, obj.color
        )
    colored_badge.short_description = "Rang"

    def post_count(self, obj):
        return obj.get_post_count()
    post_count.short_description = "Postlar soni"


class CommentInline(admin.TabularInline):
    model = Comment
    extra = 0
    fields = ['author', 'text', 'is_active', 'created_at']
    readonly_fields = ['author', 'created_at']


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'category', 'status', 'views_count', 'like_count', 'created_at']
    list_filter = ['status', 'category', 'created_at']
    search_fields = ['title', 'author__username', 'content']
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ['status']
    readonly_fields = ['views_count', 'created_at', 'updated_at']
    inlines = [CommentInline]
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Asosiy', {
            'fields': ('author', 'title', 'slug', 'category', 'status')
        }),
        ('Kontent', {
            'fields': ('excerpt', 'content', 'cover_image')
        }),
        ('Statistika', {
            'fields': ('views_count', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def like_count(self, obj):
        return obj.get_like_count()
    like_count.short_description = "❤️ Likelar"


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ['user', 'post', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'post__title']


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['author', 'post', 'short_text', 'is_reply', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['author__username', 'text', 'post__title']
    list_editable = ['is_active']
    actions = ['activate_comments', 'deactivate_comments']

    def short_text(self, obj):
        return obj.text[:60] + '...' if len(obj.text) > 60 else obj.text
    short_text.short_description = "Izoh"

    def is_reply(self, obj):
        return format_html(
            '<span style="color:{}">●</span> {}',
            '#10b981' if obj.parent else '#6366f1',
            'Reply' if obj.parent else 'Comment'
        )
    is_reply.short_description = "Turi"

    @admin.action(description="Tanlangan izohlarni faollashtirish")
    def activate_comments(self, request, queryset):
        queryset.update(is_active=True)

    @admin.action(description="Tanlangan izohlarni o'chirish")
    def deactivate_comments(self, request, queryset):
        queryset.update(is_active=False)