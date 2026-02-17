from datetime import datetime
from typing import Optional

from ninja import Schema


class CommentIn(Schema):
    text: str


class CommentOut(Schema):
    id: int
    text: str
    author_id: int
    author_username: str
    article_id: int
    created_at: datetime
    updated_at: datetime

    @staticmethod
    def resolve_author_username(obj):
        return obj.author.username


class CommentUpdate(Schema):
    text: Optional[str] = None
