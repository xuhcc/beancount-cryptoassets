from beancount.core.number import D
try:
    from beanprice import source  # noqa: F401
except ImportError:
    from beancount.prices import source  # noqa: F401

USER_AGENT = 'price-fetcher'


def to_decimal(number, precision):
    template = '{:.{p}g}'
    number_str = template.format(float(number), p=precision)
    return D(number_str)
