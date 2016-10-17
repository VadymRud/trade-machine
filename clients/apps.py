from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class ClientsConfig(AppConfig):
    name = 'clients'
    verbose_name = _('Users')
