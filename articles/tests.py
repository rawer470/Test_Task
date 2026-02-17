import json

from django.contrib.auth.models import User
from django.test import TestCase, Client

from articles.models import Article
from users.models import AuthToken


class ArticleListTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='pass')
        Article.objects.create(title='Test', content='Body', author=self.user)

    def test_list_articles(self):
        response = self.client.get('/api/articles/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)

    def test_list_articles_empty(self):
        Article.objects.all().delete()
        response = self.client.get('/api/articles/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 0)


class ArticleDetailTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='pass')
        self.article = Article.objects.create(title='Test', content='Body', author=self.user)

    def test_get_article(self):
        response = self.client.get(f'/api/articles/{self.article.id}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['title'], 'Test')

    def test_get_article_not_found(self):
        response = self.client.get('/api/articles/9999')
        self.assertEqual(response.status_code, 404)


class ArticleCreateTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='pass')
        self.token = AuthToken.objects.create(user=self.user)

    def test_create_article(self):
        response = self.client.post(
            '/api/articles/',
            data=json.dumps({'title': 'New', 'content': 'Content'}),
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Bearer {self.token.key}',
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()['title'], 'New')

    def test_create_article_unauthorized(self):
        response = self.client.post(
            '/api/articles/',
            data=json.dumps({'title': 'New', 'content': 'Content'}),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 401)


class ArticleUpdateTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='owner', password='pass')
        self.other = User.objects.create_user(username='other', password='pass')
        self.token = AuthToken.objects.create(user=self.user)
        self.other_token = AuthToken.objects.create(user=self.other)
        self.article = Article.objects.create(title='Old', content='Body', author=self.user)

    def test_update_own_article(self):
        response = self.client.put(
            f'/api/articles/{self.article.id}',
            data=json.dumps({'title': 'Updated'}),
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Bearer {self.token.key}',
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['title'], 'Updated')

    def test_update_other_article_forbidden(self):
        response = self.client.put(
            f'/api/articles/{self.article.id}',
            data=json.dumps({'title': 'Hack'}),
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Bearer {self.other_token.key}',
        )
        self.assertEqual(response.status_code, 403)


class ArticleDeleteTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='owner', password='pass')
        self.other = User.objects.create_user(username='other', password='pass')
        self.token = AuthToken.objects.create(user=self.user)
        self.other_token = AuthToken.objects.create(user=self.other)
        self.article = Article.objects.create(title='Del', content='Body', author=self.user)

    def test_delete_own_article(self):
        response = self.client.delete(
            f'/api/articles/{self.article.id}',
            HTTP_AUTHORIZATION=f'Bearer {self.token.key}',
        )
        self.assertEqual(response.status_code, 204)
        self.assertFalse(Article.objects.filter(id=self.article.id).exists())

    def test_delete_other_article_forbidden(self):
        response = self.client.delete(
            f'/api/articles/{self.article.id}',
            HTTP_AUTHORIZATION=f'Bearer {self.other_token.key}',
        )
        self.assertEqual(response.status_code, 403)
