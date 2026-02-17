from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from users.models import AuthToken


class ArticleInline(admin.TabularInline):
    from articles.models import Article
    model = Article
    fields = ('title', 'category', 'created_at')
    readonly_fields = ('created_at',)
    extra = 0
    show_change_link = True


class CommentInline(admin.TabularInline):
    from comments.models import Comment
    model = Comment
    fields = ('article', 'text', 'created_at')
    readonly_fields = ('created_at',)
    extra = 0
    show_change_link = True


class AuthTokenInline(admin.TabularInline):
    model = AuthToken
    fields = ('key', 'created_at')
    readonly_fields = ('key', 'created_at')
    extra = 0
    can_delete = True


class CustomUserAdmin(UserAdmin):
    inlines = [ArticleInline, CommentInline, AuthTokenInline]
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'date_joined')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'date_joined')


admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)


@admin.register(AuthToken)
class AuthTokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'short_key', 'created_at')
    search_fields = ('user__username',)
    readonly_fields = ('key', 'created_at')
    raw_id_fields = ('user',)

    def short_key(self, obj):
        return obj.key[:32] + '...'
    short_key.short_description = 'Token (preview)'
