import datetime
import json
import re
from urllib.parse import urljoin, urlencode
from urllib.request import Request, urlopen

from beancount.prices import source

from . import coingecko
from .utils import USER_AGENT, to_decimal

TICKER_REGEXP = re.compile(r'^(?P<address>\w+):(?P<quote>\w+)$')
API_BASE_URL = 'https://api.compound.finance'


def get_exchange_rate(token_address):
    """
    https://compound.finance/developers/api#CTokenService
    """
    path = '/api/v2/ctoken'
    url_params = {
        'addresses[]': token_address,
    }
    url = urljoin(API_BASE_URL, path) + '?' + urlencode(url_params)
    request = Request(url)
    request.add_header('Content-Type', 'application/json')
    request.add_header('Accept', 'application/json')
    # Requests without User-Agent header are blocked by CloudFlare
    request.add_header('User-Agent', USER_AGENT)
    response = urlopen(request)
    data = json.loads(response.read())
    token_data = data['cToken'][0]
    exchange_rate = token_data['exchange_rate']['value']
    symbol = token_data['symbol']
    underlying_symbol = token_data['underlying_symbol']
    return exchange_rate, symbol, underlying_symbol


class Source(source.Source):

    def _get_price(self, ticker, time=None):
        match = TICKER_REGEXP.match(ticker)
        token_address, quote_currency = match.groups()
        token_price, symbol, underlying_symbol = \
            get_exchange_rate(token_address)
        underlying_price, timestamp = coingecko.get_latest_price(
            underlying_symbol,
            quote_currency,
        )
        price = to_decimal(float(token_price) * float(underlying_price), 8)
        price_time = datetime.datetime.fromtimestamp(timestamp).\
            replace(tzinfo=datetime.timezone.utc)
        return source.SourcePrice(price, price_time, symbol)

    def get_latest_price(self, ticker):
        return self._get_price(ticker)

    def get_historical_price(self, ticker, time):
        raise NotImplementedError
