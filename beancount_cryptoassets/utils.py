from beancount.core.number import D


def to_decimal(number, precision):
    quant = D('0.' + '0' * precision)
    return D(number).quantize(quant)
