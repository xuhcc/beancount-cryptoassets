try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='beancount-cryptoassets',
    version='2.3.1',
    description='Beancount Cryptoassets',
    packages=['beancount_cryptoassets'],
    license='GPLv3',
)
