from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class FinanceConfig(AppConfig):
    name = 'finance'
    verbose_name = _('Finances')
