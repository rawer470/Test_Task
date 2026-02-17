import logging

from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from ninja import Router

from users.auth import TokenAuth
from users.models import AuthToken
from users.schemas import ErrorOut, LoginIn, MessageOut, RegisterIn, TokenOut

logger = logging.getLogger('users')

router = Router(tags=['auth'])


@router.post('/register', response={201: TokenOut, 400: ErrorOut})
def register(request, payload: RegisterIn):
    if User.objects.filter(username=payload.username).exists():
        logger.warning("Registration failed: username '%s' already exists", payload.username)
        return 400, {'detail': 'Username already exists'}

    user = User.objects.create_user(username=payload.username, password=payload.password)
    token = AuthToken.objects.create(user=user)
    logger.info("User '%s' registered successfully", user.username)
    return 201, {'token': token.key, 'username': user.username}


@router.post('/login', response={200: TokenOut, 401: ErrorOut})
def login(request, payload: LoginIn):
    user = authenticate(username=payload.username, password=payload.password)
    if user is None:
        logger.warning("Login failed for username '%s'", payload.username)
        return 401, {'detail': 'Invalid credentials'}

    token = AuthToken.objects.create(user=user)
    logger.info("User '%s' logged in", user.username)
    return 200, {'token': token.key, 'username': user.username}


@router.post('/logout', response={200: MessageOut}, auth=TokenAuth())
def logout(request):
    token_key = request.auth  # This is the user from TokenAuth
    # Delete the token used in this request
    bearer = request.headers.get('Authorization', '').replace('Bearer ', '')
    AuthToken.objects.filter(key=bearer).delete()
    logger.info("User '%s' logged out", request.auth.username)
    return 200, {'detail': 'Logged out successfully'}
