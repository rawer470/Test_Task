from django.contrib import admin
from django.urls import path
from ninja import NinjaAPI
from ninja_jwt.controller import NinjaJWTDefaultController
from ninja_extra import NinjaExtraAPI

from users.api import router as auth_router
from articles.api import router as articles_router
from comments.api import router as comments_router

api = NinjaExtraAPI(title='Blog API', version='1.0.0')
api.register_controllers(NinjaJWTDefaultController)

api.add_router('/auth', auth_router)
api.add_router('/articles', articles_router)
api.add_router('/articles', comments_router)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', api.urls),
]
