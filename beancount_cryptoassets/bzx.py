import datetime
import json
import re
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from beancount.prices import source

from . import cryptonator
from .utils import to_decimal

TICKER_REGEXP = re.compile(r'^(?P<address>0x[0-9a-f]{40}):(?P<quote>\w+)$')


def eth_call(to, data, result_type):
    """
    https://etherscan.io/apis#proxy
    """
    base_url = 'https://api.etherscan.io/api'
    url_params = {
        'module': 'proxy',
        'action': 'eth_call',
        'to': to,
        'data': data,
    }
    url = base_url + '?' + urlencode(url_params)
    request = Request(url)
    request.add_header('Content-Type', 'application/json')
    request.add_header('Accept', 'application/json')
    response = urlopen(request)
    data = json.loads(response.read())
    result = data['result']
    if result_type == 'uint256':
        return int(result, 16)
    elif result_type == 'string':
        # https://github.com/ethereum/eth-abi/blob/v2.1.0/eth_abi/decoding.py#L543
        result_bin = bytes.fromhex(result[2:])
        length = int.from_bytes(result_bin[32:64], 'big')
        return result_bin[64:][:length].decode('utf-8')
    else:
        raise ValueError


def get_exchange_rate(token_address):
    """
    Get exchange rate for iToken
    """
    exchange_rate = eth_call(
        token_address,
        '0x7ff9b596',  # tokenPrice()
        'uint256',
    )
    symbol = eth_call(
        token_address,
        '0x95d89b41',  # symbol()
        'string',
    )
    return exchange_rate / 10 ** 18, symbol


class Source(source.Source):

    def _get_price(self, ticker, time=None):
        match = TICKER_REGEXP.match(ticker)
        token_address, quote_currency = match.groups()
        token_price, symbol = get_exchange_rate(token_address)
        underlying_price, timestamp = cryptonator.get_latest_price(
            symbol[1:],  # iDAI -> DAI
            quote_currency,
        )
        price = to_decimal(token_price * float(underlying_price), 8)
        price_time = datetime.datetime.fromtimestamp(timestamp).\
            replace(tzinfo=datetime.timezone.utc)
        return source.SourcePrice(price, price_time, symbol)

    def get_latest_price(self, ticker):
        return self._get_price(ticker)

    def get_historical_price(self, ticker, time):
        raise NotImplementedError
