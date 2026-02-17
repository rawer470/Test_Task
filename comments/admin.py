from django.contrib import admin

from comments.models import Comment


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'author', 'article', 'short_text', 'created_at', 'updated_at')
    list_filter = ('created_at', 'author')
    search_fields = ('text', 'author__username', 'article__title')
    readonly_fields = ('created_at', 'updated_at')
    raw_id_fields = ('author', 'article')

    def short_text(self, obj):
        return obj.text[:60] + '...' if len(obj.text) > 60 else obj.text
    short_text.short_description = 'Text'
