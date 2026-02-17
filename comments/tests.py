import json

from django.contrib.auth.models import User
from django.test import TestCase, Client

from articles.models import Article
from comments.models import Comment
from users.models import AuthToken


class CommentListTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='pass')
        self.article = Article.objects.create(title='Art', content='Body', author=self.user)
        Comment.objects.create(text='Nice', author=self.user, article=self.article)

    def test_list_comments(self):
        response = self.client.get(f'/api/articles/{self.article.id}/comments')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)

    def test_list_comments_wrong_article(self):
        response = self.client.get('/api/articles/9999/comments')
        self.assertEqual(response.status_code, 404)


class CommentDetailTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='pass')
        self.article = Article.objects.create(title='Art', content='Body', author=self.user)
        self.comment = Comment.objects.create(text='Nice', author=self.user, article=self.article)

    def test_get_comment(self):
        response = self.client.get(
            f'/api/articles/{self.article.id}/comments/{self.comment.id}'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['text'], 'Nice')

    def test_get_comment_not_found(self):
        response = self.client.get(
            f'/api/articles/{self.article.id}/comments/9999'
        )
        self.assertEqual(response.status_code, 404)


class CommentCreateTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='pass')
        self.token = AuthToken.objects.create(user=self.user)
        self.article = Article.objects.create(title='Art', content='Body', author=self.user)

    def test_create_comment(self):
        response = self.client.post(
            f'/api/articles/{self.article.id}/comments',
            data=json.dumps({'text': 'Great post!'}),
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Bearer {self.token.key}',
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()['text'], 'Great post!')

    def test_create_comment_unauthorized(self):
        response = self.client.post(
            f'/api/articles/{self.article.id}/comments',
            data=json.dumps({'text': 'Great post!'}),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 401)


class CommentUpdateTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='owner', password='pass')
        self.other = User.objects.create_user(username='other', password='pass')
        self.token = AuthToken.objects.create(user=self.user)
        self.other_token = AuthToken.objects.create(user=self.other)
        self.article = Article.objects.create(title='Art', content='Body', author=self.user)
        self.comment = Comment.objects.create(text='Old', author=self.user, article=self.article)

    def test_update_own_comment(self):
        response = self.client.put(
            f'/api/articles/{self.article.id}/comments/{self.comment.id}',
            data=json.dumps({'text': 'Updated'}),
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Bearer {self.token.key}',
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['text'], 'Updated')

    def test_update_other_comment_forbidden(self):
        response = self.client.put(
            f'/api/articles/{self.article.id}/comments/{self.comment.id}',
            data=json.dumps({'text': 'Hack'}),
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Bearer {self.other_token.key}',
        )
        self.assertEqual(response.status_code, 403)


class CommentDeleteTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='owner', password='pass')
        self.other = User.objects.create_user(username='other', password='pass')
        self.token = AuthToken.objects.create(user=self.user)
        self.other_token = AuthToken.objects.create(user=self.other)
        self.article = Article.objects.create(title='Art', content='Body', author=self.user)
        self.comment = Comment.objects.create(text='Del', author=self.user, article=self.article)

    def test_delete_own_comment(self):
        response = self.client.delete(
            f'/api/articles/{self.article.id}/comments/{self.comment.id}',
            HTTP_AUTHORIZATION=f'Bearer {self.token.key}',
        )
        self.assertEqual(response.status_code, 204)
        self.assertFalse(Comment.objects.filter(id=self.comment.id).exists())

    def test_delete_other_comment_forbidden(self):
        response = self.client.delete(
            f'/api/articles/{self.article.id}/comments/{self.comment.id}',
            HTTP_AUTHORIZATION=f'Bearer {self.other_token.key}',
        )
        self.assertEqual(response.status_code, 403)
