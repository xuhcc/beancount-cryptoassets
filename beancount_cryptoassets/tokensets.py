import datetime
import json
import re
from urllib.parse import urljoin
from urllib.request import Request, urlopen

from beancount.prices import source

from .utils import to_decimal

TICKER_REGEXP = re.compile(r'^(?P<base>\w+):(?P<quote>USD)$')
API_BASE_URL = 'https://api.tokensets.com/'


def get_data(set_symbol):
    path = '/v1/rebalancing_sets/{}'.format(set_symbol.lower())
    url = urljoin(API_BASE_URL, path)
    request = Request(url)
    # Requests without User-Agent header are blocked by CloudFlare
    request.add_header('User-Agent', 'price-fetcher')
    response = urlopen(request)
    data = json.loads(response.read())
    return data


class Source(source.Source):

    def _get_price(self, ticker, time=None):
        match = TICKER_REGEXP.match(ticker)
        base_currency, quote_currency = match.groups()
        data = get_data(base_currency)

        if time is None:
            price_str = data['rebalancing_set']['price_usd']
            price = to_decimal(price_str, 6)
            price_time = datetime.datetime.now(tz=datetime.timezone.utc)
        else:
            time_utc = time.astimezone(datetime.timezone.utc)
            sorted_prices = sorted(zip(
                data['rebalancing_set']['historicals']['dates'],
                data['rebalancing_set']['historicals']['prices'],
            ), key=lambda item: item[0])
            for price_time_str, price_str in sorted_prices:
                price_time = datetime.datetime.strptime(
                    price_time_str,
                    '%Y-%m-%dT%H:%M:%SZ',
                ).replace(tzinfo=datetime.timezone.utc)
                if price_time.date() == time_utc.date() \
                        and price_time > time_utc:
                    price = to_decimal(price_str, 6)
                    break
            else:
                return None

        return source.SourcePrice(price, price_time, base_currency)

    def get_latest_price(self, ticker):
        return self._get_price(ticker)

    def get_historical_price(self, ticker, time):
        return self._get_price(ticker, time)
