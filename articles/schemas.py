from datetime import datetime
from typing import Optional

from ninja import Schema


class ArticleIn(Schema):
    title: str
    content: str
    category_id: Optional[int] = None


class ArticleOut(Schema):
    id: int
    title: str
    content: str
    author_id: int
    author_username: str
    category_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    @staticmethod
    def resolve_author_username(obj):
        return obj.author.username


class ArticleUpdate(Schema):
    title: Optional[str] = None
    content: Optional[str] = None
    category_id: Optional[int] = None
