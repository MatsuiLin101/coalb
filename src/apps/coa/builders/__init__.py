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
    CropPriceOriginBuilder().build()
    CropPriceWholesaleBuilder().build()
    CropProduceTotalBuilder().build()

    # 目前部署後無法執行
    CropCostBuilder().build()
