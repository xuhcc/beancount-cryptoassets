# Beancount Cryptoassets

Price sources for [Beancount](http://furius.ca/beancount/) that provide prices for various cryptoassets.

## Installation

Install latest version with `pip`:

```
pip install https://github.com/xuhcc/beancount-cryptoassets/archive/master.zip
```

## Coinmarketcap Pro API

API key is required. You can get free one at https://pro.coinmarketcap.com/ but it grants access only to latest quotes.

Source string format is `<quote-currency>:beancount_cryptoassets.coinmarketcap_api/<api-key>:<base-currency>:<quote-currency>`.

## Examples

Evaluate source string with `bean-price`:

```
bean-price --no-cache -e 'USD:beancount_cryptoassets.coinmarketcap_api/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx:BTC:USD'
```

Set price source for commodity in beancount file:

```
2009-01-09 commodity BTC
    price: "USD:beancount_cryptoassets.coinmarketcap_api/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx:BTC:USD"
```
