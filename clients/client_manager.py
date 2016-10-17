from django.contrib.auth.models import AnonymousUser
from django.contrib.auth import get_user as get_admin
from rest_framework.authtoken.models import Token
from finance.models import Wallet, Currency
from django.utils.functional import SimpleLazyObject


def user_by_token(token):
    try:
        token_object = Token.objects.filter(key__exact=token).select_related('user').get()
    except Token.DoesNotExist:
        return None

    return token_object.user


def get(request):
    # if admin is auth
    admin = get_admin(request)
    if not isinstance(admin, AnonymousUser):
        return admin

    token = request.COOKIES.get('token')
    if token is None:
        return AnonymousUser()

    return user_by_token(token) or AnonymousUser()


def get_user(request):
    if not hasattr(request, '_cached_user'):
        request._cached_user = get(request)
    return request._cached_user


class AuthenticationMiddleware(object):
    @staticmethod
    def process_request(request):
        assert hasattr(request, 'session'), (
            "The Django authentication middleware requires session middleware "
            "to be installed. Edit your MIDDLEWARE_CLASSES setting to insert "
            "'django.contrib.sessions.middleware.SessionMiddleware' before "
            "'django.contrib.auth.middleware.AuthenticationMiddleware'."
        )
        request.user = SimpleLazyObject(lambda: get_user(request))
