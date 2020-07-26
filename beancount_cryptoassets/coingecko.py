import datetime
import json
import re
from functools import lru_cache
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from beancount.prices import source

from .utils import to_decimal

TICKER_REGEXP = re.compile(r'^(?P<base>\w+):(?P<quote>\w+)$')
API_BASE_URL = 'https://api.coingecko.com/api/v3'


@lru_cache
def _get_coin_list():
    """
    Get mapping between the symbol and coin ID
    """
    path = '/coins/list/'
    url = API_BASE_URL + path
    request = Request(url)
    response = urlopen(request)
    data = json.loads(response.read())
    return {item['symbol']: item['id'] for item in data}


def get_latest_price(base_currency, quote_currency):
    """
    https://www.coingecko.com/api/documentations/v3
    """
    path = '/simple/price/'
    base_currency_id = _get_coin_list()[base_currency.lower()]
    url_params = {
        'ids':  base_currency_id,
        'vs_currencies': quote_currency.lower(),
        'include_last_updated_at': 'true',
    }
    url = API_BASE_URL + path + '?' + urlencode(url_params)
    request = Request(url)
    response = urlopen(request)
    data = json.loads(response.read())
    price_float = data[base_currency_id][quote_currency.lower()]
    timestamp = data[base_currency_id]['last_updated_at']
    return price_float, timestamp


class Source(source.Source):

    def _get_price(self, ticker, time=None):
        match = TICKER_REGEXP.match(ticker)
        base_currency, quote_currency = match.groups()
        price_float, timestamp = get_latest_price(base_currency,
                                                  quote_currency)

        price = to_decimal(price_float, 8)
        price_time = datetime.datetime.fromtimestamp(timestamp).\
            replace(tzinfo=datetime.timezone.utc)
        return source.SourcePrice(price, price_time, base_currency)

    def get_latest_price(self, ticker):
        return self._get_price(ticker)

    def get_historical_price(self, ticker, time):
        raise NotImplementedError
