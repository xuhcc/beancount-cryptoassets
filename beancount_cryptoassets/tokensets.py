import datetime
import json
import re
from urllib.parse import urljoin
from urllib.request import Request, urlopen

from beancount.prices import source

from .utils import to_decimal

TICKER_REGEXP = re.compile(r'^(?P<base>\w+):(?P<quote>USD)$')
API_BASE_URL = 'https://api.tokensets.com/'


def get_latest_price(set_symbol):
    path = '/v1/rebalancing_sets/{}'.format(set_symbol.lower())
    url = urljoin(API_BASE_URL, path)
    request = Request(url)
    # Requests without User-Agent header are blocked by CloudFlare
    request.add_header('User-Agent', 'price-fetcher')
    response = urlopen(request)
    result = json.loads(response.read())
    price_str = result['rebalancing_set']['price_usd']
    return to_decimal(price_str, 6)


class Source(source.Source):

    def _get_price(self, ticker, time=None):
        match = TICKER_REGEXP.match(ticker)
        base_currency, quote_currency = match.groups()
        price = get_latest_price(base_currency)
        price_time = datetime.datetime.now(tz=datetime.timezone.utc)
        return source.SourcePrice(price, price_time, base_currency)

    def get_latest_price(self, ticker):
        return self._get_price(ticker)

    def get_historical_price(self, ticker, time):
        raise NotImplementedError
