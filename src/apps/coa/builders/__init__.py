from .producevalue import *
from .livestockfeedlot import *
from .livestockfeedamount import *
from .livestockslaughter import *
from .livestockbyproduct import *
from .cropcost import *
from .cropprice import *
from .cropproduce import *


def build():
    TotalValueBuilder().build()
    LivestockFeedlotBuilder().build()
    LivestockFeedamountBuilder().build()
    LivestockSlaughterBuilder().build()
    LivestockByproductBuilder().build()
    CropCostBuilder().build()
    CropPriceOriginBuilder().build()
    CropPriceWholesaleBuilder().build()
    CropProduceTotalBuilder().build()
