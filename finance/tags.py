from django.conf import settings
from django.template.loader_tags import register


@register.inclusion_tag('custom/wallets.html')
def show_users_wallets(request):
    result = {'wallets': []}

    from finance.models import Wallet
    wallets = Wallet.objects.filter(client=request.user). \
        values('balance', 'balance_reserve', 'currency__short_name').all()

    for item in wallets:
        available = float(item['balance'] - item['balance_reserve'])

        if available < settings.DECIMAL_EPSILON:
            available = 0

        result['wallets'].append({
            'currency': item['currency__short_name'],
            'amount': available
        })

    return result
