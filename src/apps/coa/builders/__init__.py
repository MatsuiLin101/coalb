from .cropcost import *
from .cropprice import *
from .cropproduce import *


def build():
    CropCostBuilder().build()
    CropPriceOriginBuilder().build()
    CropPriceWholesaleBuilder().build()
    CropProduceTotalBuilder().build()
