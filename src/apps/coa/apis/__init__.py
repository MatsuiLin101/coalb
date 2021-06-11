"""
coa.apis package
"""

from .value import ValueApiView
'''
總產值修改縣市查詢規則，有完全符合的就不檢查其他選項
台南市
台灣省台南市
'''

from .gross import GrossApiView

from .income import IncomeApiView

from .farmer import FarmerApiView

from .farmerarea import FarmerAreaApiView

from .laborforce import LaborforceApiView

from .disaster import DisasterApiView
'''
數字加上逗點區隔
'''

from .welfare import WelfareApiView
'''
Scholarship無法查詢到縣市
'''

# from .cropprice import CropPriceApiView

# from .cropproduce import CropProduceApiView

# from .cropcost import CropCostApiView

from .livestockhog import LivestockHogApiView
'''
是否更改指令統一為「毛豬」
'''

# from .livestockprice import LivestockPriceApiView
'''
dev
'''

# from .livestockfeedlot import LivestockFeedlotApiView

# from .livestockfeedamount import LivestockFeedamountApiView

# from .livestockslaughter import LivestockSlaughterApiView

# from .livestockbyproduct import LivestockByproductApiView

# from .productcode import ProductCodeApiView
