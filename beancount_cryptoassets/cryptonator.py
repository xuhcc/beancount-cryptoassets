import datetime
import json
import re
from urllib.parse import urljoin
from urllib.request import Request, urlopen

from beancount.prices import source

from .utils import USER_AGENT, to_decimal

TICKER_REGEXP = re.compile(r'^(?P<base>\w+):(?P<quote>\w+)$')
API_BASE_URL = 'https://api.cryptonator.com'


def get_latest_price(base_currency, quote_currency):
    """
    https://www.cryptonator.com/api
    """
    path = '/api/ticker/{base}-{quote}'.format(
        base=base_currency.lower(),
        quote=quote_currency.lower(),
    )
    url = urljoin(API_BASE_URL, path)
    request = Request(url)
    # Requests without User-Agent header are blocked by Cryptonator
    request.add_header('User-Agent', USER_AGENT)
    response = urlopen(request)
    data = json.loads(response.read())
    if data['success'] is not True:
        error_message = '{0} ({1}:{2})'.format(
            data['error'],
            base_currency,
            quote_currency,
        )
        raise ValueError(error_message)
    price_str = data['ticker']['price']
    timestamp = data['timestamp']
    return price_str, timestamp


class Source(source.Source):

    def _get_price(self, ticker, time=None):
        match = TICKER_REGEXP.match(ticker)
        base_currency, quote_currency = match.groups()
        price_str, timestamp = get_latest_price(base_currency, quote_currency)

        price = to_decimal(price_str, 8)
        price_time = datetime.datetime.fromtimestamp(timestamp).\
            replace(tzinfo=datetime.timezone.utc)
        return source.SourcePrice(price, price_time, base_currency)

    def get_latest_price(self, ticker):
        return self._get_price(ticker)

    def get_historical_price(self, ticker, time):
        raise NotImplementedError
