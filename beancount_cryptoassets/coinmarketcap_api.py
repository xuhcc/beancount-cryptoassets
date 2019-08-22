import datetime
import json
import re
from urllib.parse import urljoin, urlencode
from urllib.request import Request, urlopen

from beancount.prices import source

from .utils import to_decimal

TICKER_REGEXP = re.compile(r'^(?P<key>[\w-]+):(?P<base>\w+):(?P<quote>\w+)$')
API_BASE_URL = 'https://pro-api.coinmarketcap.com/'


def get_latest_quote(api_key, base_currency, quote_currency):
    path = '/v1/cryptocurrency/quotes/latest'
    url_params = {
        'symbol': base_currency,
        'convert': quote_currency,
    }
    url = urljoin(API_BASE_URL, path) + '?' + urlencode(url_params)
    request = Request(url)
    request.add_header('X-CMC_PRO_API_KEY', api_key)
    response = urlopen(request)
    result = json.loads(response.read())
    return result['data'][base_currency]['quote'][quote_currency]


class Source(source.Source):

    def _get_price(self, ticker, time=None):
        match = TICKER_REGEXP.match(ticker)
        api_key, base_currency, quote_currency = match.groups()
        data = get_latest_quote(api_key, base_currency, quote_currency)

        price = to_decimal(data['price'], 8)
        price_time = datetime.datetime.strptime(
            data['last_updated'],
            '%Y-%m-%dT%H:%M:%S.%fZ',
        ).replace(tzinfo=datetime.timezone.utc)
        return source.SourcePrice(price, price_time, base_currency)

    def get_latest_price(self, ticker):
        return self._get_price(ticker)

    def get_historical_price(self, ticker, time):
        raise NotImplementedError
