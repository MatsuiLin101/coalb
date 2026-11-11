from .livestockslaughter import *
from .livestockbyproduct import *
from .cropcost import *
from .cropprice import *
from .cropproduce import *


def build():
    LivestockSlaughterBuilder().build()
    LivestockByproductBuilder().build()
    CropCostBuilder().build()
    CropPriceOriginBuilder().build()
    CropPriceWholesaleBuilder().build()
    CropProduceTotalBuilder().build()
