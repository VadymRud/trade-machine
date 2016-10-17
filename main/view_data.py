from finance.models import Pair, Exchange
from .models import News


class PairViewData:
    pair = None

    def __init__(self, name=None):
        self.pairs = Pair.objects.filter(active__exact=True).all()

        if len(self.pairs) > 0:
            self.pair = self.pairs[0]

        if name:
            for p in self.pairs:
                if p.name == name:
                    self.pair = p

    @property
    def rate(self):
        if self.pair is None:
            return 0

        last_exchange = Exchange.objects.values('price').filter(pair=self.pair).last()

        if last_exchange is None:
            return 0
        else:
            return last_exchange['price']

    @staticmethod
    def get_last_news():
        return News.objects.order_by('date')[:5]
