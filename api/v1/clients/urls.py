from django.conf.urls import url

from rest_framework.authtoken.views import ObtainAuthToken

urlpatterns = [
    url(r'^token/', ObtainAuthToken.as_view(), name='token')
]
