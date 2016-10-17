from django.conf.urls import include, url
from django.conf import settings
from django.contrib import admin
from django.views.defaults import *
from django.conf.urls.static import static

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url('^', include('main.urls'), name='web'),
    url('^api/v1/', include('api.v1.urls', namespace='v1')),
    url(r'^i18n/', include('django.conf.urls.i18n')),
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^rosetta/', include('rosetta.urls')),
    url(r'^captcha/', include('captcha.urls')),


] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) + \
              static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
