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
待確認
數字加上逗點區隔
'''

from .welfare import WelfareApiView
'''
待修正
Scholarship無法查詢到縣市
'''

# from .cropprice import CropPriceApiView

from .cropproduce import CropProduceApiView
'''
待開發
單位產值
單位產量

待測試
產量
種植面積

待修正
作物太多查詢時間過長會導致reply_token失效(30秒)
'''

# from .cropcost import CropCostApiView

from .livestockhog import LivestockHogApiView
'''
是否更改指令統一為「毛豬」
'''

from .livestockprice import LivestockPriceApiView
'''
待測試
本次測試正常
部署後無法使用需要除錯
'''

from .livestockfeedlot import LivestockFeedlotApiView
'''
已開發完成待測試
'''

# from .livestockfeedamount import LivestockFeedamountApiView

# from .livestockslaughter import LivestockSlaughterApiView

# from .livestockbyproduct import LivestockByproductApiView

# from .productcode import ProductCodeApiView
