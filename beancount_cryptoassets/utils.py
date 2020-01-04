from beancount.core.number import D

USER_AGENT = 'price-fetcher'


def to_decimal(number, precision):
    template = '{:.{p}g}'
    number_str = template.format(float(number), p=precision)
    return D(number_str)
