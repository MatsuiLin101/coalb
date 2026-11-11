from .livestockfeedamount import *
from .livestockslaughter import *
from .livestockbyproduct import *
from .cropcost import *
from .cropprice import *
from .cropproduce import *


def build():
    LivestockFeedAmountBuilder().build()
    LivestockSlaughterBuilder().build()
    LivestockByproductBuilder().build()
    CropCostBuilder().build()
    CropPriceOriginBuilder().build()
    CropPriceWholesaleBuilder().build()
    CropProduceTotalBuilder().build()
