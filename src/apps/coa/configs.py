from .utils import get_driver


class ApiView(object):
    '''
    Basic view for coa apis
    '''
    def __init__(self, url, key, year, product='', city=''):
        self.url = url
        self.key = key
        self.year = year
        self.product = product
        self.city = city

    def fname(arg):
        pass
