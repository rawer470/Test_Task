from ninja.security import HttpBearer

from users.models import AuthToken


class TokenAuth(HttpBearer):
    def authenticate(self, request, token: str):
        try:
            auth_token = AuthToken.objects.select_related('user').get(key=token)
            return auth_token.user
        except AuthToken.DoesNotExist:
            return None
