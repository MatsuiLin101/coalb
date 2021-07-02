from .livestockfeedlot import *
from .livestockfeedamount import *
from .livestockslaughter import *
from .livestockbyproduct import *
from .cropcost import *
from .cropprice import *


def build():
    LivestockFeedlotBuilder().build()
    LivestockFeedamountBuilder().build()
    LivestockSlaughterBuilder().build()
    LivestockByproductBuilder().build()
    CropCostBuilder().build()
    CropPriceOriginBuilder().build()
    CropPriceWholesaleBuilder().build()
