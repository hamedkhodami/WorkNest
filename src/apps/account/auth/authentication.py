from rest_framework import exceptions
from rest_framework_simplejwt.authentication import JWTAuthentication

from apps.core import text


class BaseJWTAuthentication(JWTAuthentication):

    def authenticate(self, request, *args, **kwargs):
        auth = super().authenticate(request)
        if not auth:
            return None
        user, token = auth
        if getattr(user, "is_blocked", False):
            raise exceptions.AuthenticationFailed(text.user_blocked, code='user_blocked')
        return user, token
