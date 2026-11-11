from .cropprice import *
from .cropproduce import *


def build():
    CropPriceOriginBuilder().build()
    CropPriceWholesaleBuilder().build()
    CropProduceTotalBuilder().build()
