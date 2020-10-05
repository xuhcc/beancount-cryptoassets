import datetime
import json
import re
from urllib.request import Request, urlopen

from . import coingecko
from .utils import to_decimal, source

TICKER_REGEXP = re.compile(
    r'^(?P<api_key>[0-9a-f]{32}):(?P<address>0x[0-9a-f]{40}):(?P<quote>\w+)$'
)


def eth_call(api_key, contract_address, tx_data, result_type):
    """
    https://infura.io/docs/ethereum/json-rpc/eth_call
    """
    base_url = 'https://mainnet.infura.io/v3/{}'.format(api_key)
    params = {
        'jsonrpc': '2.0',
        'id': 1,
        'method': 'eth_call',
        'params': [
            {'to': contract_address, 'data': tx_data},
            'latest',
        ],
    }
    request = Request(
        base_url,
        data=json.dumps(params).encode(),
        method='POST',
    )
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


def get_exchange_rate(api_key, token_address):
    """
    Get exchange rate for iToken
    """
    exchange_rate = eth_call(
        api_key,
        token_address,
        '0x7ff9b596',  # tokenPrice()
        'uint256',
    )
    symbol = eth_call(
        api_key,
        token_address,
        '0x95d89b41',  # symbol()
        'string',
    )
    return exchange_rate / 10 ** 18, symbol


class Source(source.Source):

    def _get_price(self, ticker, time=None):
        match = TICKER_REGEXP.match(ticker)
        api_key, token_address, quote_currency = match.groups()
        token_price, symbol = get_exchange_rate(api_key, token_address)
        underlying_price, timestamp = coingecko.get_latest_price(
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
