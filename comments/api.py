import logging
from typing import List

from django.shortcuts import get_object_or_404
from ninja import Router

from articles.models import Article
from comments.models import Comment
from comments.schemas import CommentIn, CommentOut, CommentUpdate
from users.auth import TokenAuth
from users.schemas import ErrorOut

logger = logging.getLogger('comments')

router = Router(tags=['comments'])


@router.get('/{article_id}/comments', response=List[CommentOut])
def list_comments(request, article_id: int):
    get_object_or_404(Article, id=article_id)
    return Comment.objects.select_related('author').filter(article_id=article_id)


@router.get('/{article_id}/comments/{comment_id}', response=CommentOut)
def get_comment(request, article_id: int, comment_id: int):
    return get_object_or_404(
        Comment.objects.select_related('author'),
        id=comment_id,
        article_id=article_id,
    )


@router.post('/{article_id}/comments', response={201: CommentOut}, auth=TokenAuth())
def create_comment(request, article_id: int, payload: CommentIn):
    article = get_object_or_404(Article, id=article_id)
    comment = Comment.objects.create(
        text=payload.text,
        author=request.auth,
        article=article,
    )
    logger.info(
        "Comment %d created by user '%s' on article %d",
        comment.id, request.auth.username, article_id,
    )
    return 201, comment


@router.put('/{article_id}/comments/{comment_id}', response={200: CommentOut, 403: ErrorOut}, auth=TokenAuth())
def update_comment(request, article_id: int, comment_id: int, payload: CommentUpdate):
    comment = get_object_or_404(Comment, id=comment_id, article_id=article_id)
    if comment.author != request.auth:
        logger.warning(
            "User '%s' tried to update comment %d owned by '%s'",
            request.auth.username, comment_id, comment.author.username,
        )
        return 403, {'detail': 'You can only edit your own comments'}

    for attr, value in payload.dict(exclude_unset=True).items():
        setattr(comment, attr, value)
    comment.save()
    logger.info("Comment %d updated by user '%s'", comment_id, request.auth.username)
    return 200, comment


@router.delete('/{article_id}/comments/{comment_id}', response={204: None, 403: ErrorOut}, auth=TokenAuth())
def delete_comment(request, article_id: int, comment_id: int):
    comment = get_object_or_404(Comment, id=comment_id, article_id=article_id)
    if comment.author != request.auth:
        logger.warning(
            "User '%s' tried to delete comment %d owned by '%s'",
            request.auth.username, comment_id, comment.author.username,
        )
        return 403, {'detail': 'You can only delete your own comments'}

    comment.delete()
    logger.info("Comment %d deleted by user '%s'", comment_id, request.auth.username)
    return 204, None
