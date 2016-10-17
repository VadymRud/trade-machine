from django.conf.urls import include
from django.conf.urls import url

urlpatterns = [
    url('^', include('api.v1.clients.urls')),
    url('^', include('api.v1.finance.urls')),
]
