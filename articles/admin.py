from django.contrib import admin

from articles.models import Article


class CommentInline(admin.TabularInline):
    from comments.models import Comment
    model = Comment
    fields = ('author', 'text', 'created_at')
    readonly_fields = ('author', 'created_at')
    extra = 0
    show_change_link = True


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    inlines = [CommentInline]
    list_display = ('title', 'author', 'category', 'comment_count', 'created_at', 'updated_at')
    list_filter = ('category', 'created_at', 'author')
    search_fields = ('title', 'content', 'author__username')
    readonly_fields = ('created_at', 'updated_at')
    raw_id_fields = ('author',)
    date_hierarchy = 'created_at'

    def comment_count(self, obj):
        return obj.comments.count()
    comment_count.short_description = 'Comments'
