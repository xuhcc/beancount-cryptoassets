# Beancount Cryptoassets

Price sources for [Beancount](http://furius.ca/beancount/) that provide prices for various cryptoassets.

## Installation

Install latest version with `pip` (python 3 is required):

```
pip install https://github.com/xuhcc/beancount-cryptoassets/archive/master.zip
```

## CoinGecko API

https://www.coingecko.com/en/api

No API key required, only latest quotes.

Source string format is `<quote-currency>:beancount_cryptoassets.coingecko/<base-currency>:<quote-currency>`.

`base_currency` can be either CoinGecko currency ID (e.g. `uniswap`) or a symbol (e.g. `UNI`).

## Examples

Evaluate source string with `bean-price`:

```
PYTHONPATH=.:$PYTHONPATH bean-price --no-cache -e 'USD:beancount_cryptoassets.coingecko/BTC:USD'
```

Set price source for commodity in beancount file:

```
2009-01-09 commodity BTC
    price: "USD:beancount_cryptoassets.coingecko/BTC:USD"
```
