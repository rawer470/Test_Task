import logging
from typing import List

from django.shortcuts import get_object_or_404
from ninja import Router

from articles.models import Article
from articles.schemas import ArticleIn, ArticleOut, ArticleUpdate
from users.auth import TokenAuth
from users.schemas import ErrorOut

logger = logging.getLogger('articles')

router = Router(tags=['articles'])


@router.get('/', response=List[ArticleOut])
def list_articles(request):
    return Article.objects.select_related('author').all()


@router.get('/{article_id}', response=ArticleOut)
def get_article(request, article_id: int):
    return get_object_or_404(Article.objects.select_related('author'), id=article_id)


@router.post('/', response={201: ArticleOut}, auth=TokenAuth())
def create_article(request, payload: ArticleIn):
    article = Article.objects.create(author=request.auth, **payload.dict())
    logger.info("Article '%s' created by user '%s'", article.title, request.auth.username)
    return 201, article


@router.put('/{article_id}', response={200: ArticleOut, 403: ErrorOut}, auth=TokenAuth())
def update_article(request, article_id: int, payload: ArticleUpdate):
    article = get_object_or_404(Article, id=article_id)
    if article.author != request.auth:
        logger.warning(
            "User '%s' tried to update article %d owned by '%s'",
            request.auth.username, article_id, article.author.username,
        )
        return 403, {'detail': 'You can only edit your own articles'}

    for attr, value in payload.dict(exclude_unset=True).items():
        setattr(article, attr, value)
    article.save()
    logger.info("Article %d updated by user '%s'", article_id, request.auth.username)
    return 200, article


@router.delete('/{article_id}', response={204: None, 403: ErrorOut}, auth=TokenAuth())
def delete_article(request, article_id: int):
    article = get_object_or_404(Article, id=article_id)
    if article.author != request.auth:
        logger.warning(
            "User '%s' tried to delete article %d owned by '%s'",
            request.auth.username, article_id, article.author.username,
        )
        return 403, {'detail': 'You can only delete your own articles'}

    article.delete()
    logger.info("Article %d deleted by user '%s'", article_id, request.auth.username)
    return 204, None
