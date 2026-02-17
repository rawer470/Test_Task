from django.conf import settings
from django.db import models


class Comment(models.Model):
    text = models.TextField()
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='comments',
    )
    article = models.ForeignKey(
        'articles.Article',
        on_delete=models.CASCADE,
        related_name='comments',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Comment by {self.author.username} on {self.article.title}"
