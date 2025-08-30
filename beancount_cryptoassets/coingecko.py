import datetime
import json
import os
import re
import time
from functools import lru_cache
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from .utils import to_decimal, source

TICKER_REGEXP = re.compile(r'^(?P<base>[\w-]+):(?P<quote>\w+)$')
API_BASE_URL = 'https://api.coingecko.com/api/v3'

REQUEST_DELAY = float(os.environ.get('COINGECKO_REQUEST_DELAY', '0'))


def _get_response(request):
    if REQUEST_DELAY:
        # Wait before sending request
        time.sleep(REQUEST_DELAY)
    response = urlopen(request).read()
    return response


@lru_cache
def _get_coin_list() -> list:
    """
    Get list of currencies supported by CoinGecko
    """
    path = '/coins/list/'
    url = API_BASE_URL + path
    request = Request(url)
    response = _get_response(request)
    data = json.loads(response)
    return data


@lru_cache
def _get_currency_id(currency: str) -> str:
    """
    Find currency ID by its symbol.
    If results are ambiguous, select currency with the highest market cap
    """
    candidates = [coin['id'] for coin in _get_coin_list()
                  if coin['symbol'] == currency.lower()]
    url_params = {
        'ids':  ','.join(candidates),
        'vs_currency': 'USD',
    }
    url = f'{API_BASE_URL}/coins/markets?{urlencode(url_params)}'
    request = Request(url)
    response = _get_response(request)
    data = json.loads(response)
    if not data:
        raise RuntimeError(response)
    if len(data) == 1:
        return data[0]['id']
    # Sort by market cap
    keyfunc = lambda item: item['market_cap_rank'] or 100000
    top_result = list(sorted(data, key=keyfunc))[0]
    if top_result['market_cap_rank'] is None:
        raise RuntimeError(
            f'Try to use currency ID instead of symbol ({currency}).'
        )
    return top_result['id']


def get_latest_price(base_currency, quote_currency):
    """
    https://www.coingecko.com/api/documentations/v3
    """
    path = '/simple/price/'
    if base_currency.isupper():
        # Try to find currency ID by its symbol
        base_currency_id = _get_currency_id(base_currency)
    else:
        base_currency_id = base_currency
    url_params = {
        'ids':  base_currency_id,
        'vs_currencies': quote_currency.lower(),
        'include_last_updated_at': 'true',
    }
    url = API_BASE_URL + path + '?' + urlencode(url_params)
    request = Request(url)
    response = _get_response(request)
    data = json.loads(response)
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
