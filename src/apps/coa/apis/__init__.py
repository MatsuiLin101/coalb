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

from .cropprice import CropPriceApiView
'''
指令
產地價
批發價

已開發完成待測試

待修正
產地價 - 部署後無法使用需要除錯
'''

from .cropproduce import CropProduceApiView
'''
指令
產量
種植面積
單位產值
單位產量

已開發完成待測試

待開發
合併「產量」「種植面積」指令
合併「單位產值」「單位產量」指令

待修正
「產量」「種植面積」 - 作物太多查詢時間過長會導致reply_token失效(30秒)
'''

from .cropcost import CropCostApiView
'''
已開發完成待測試
'''

from .livestockhog import LivestockHogApiView
'''
待開發
更改指令統一為「毛豬」
'''

from .livestockprice import LivestockPriceApiView
'''
已開發完成待測試

待修正
部署後無法使用需要除錯
'''

from .livestockfeedlot import LivestockFeedlotApiView
'''
已開發完成待測試
'''

from .livestockfeedamount import LivestockFeedamountApiView
'''
已開發完成待測試
'''

from .livestockslaughter import LivestockSlaughterApiView
'''
reviewed
已開發完成待測試
'''

from .livestockbyproduct import LivestockByproductApiView
'''
已開發完成待測試

待開發
原指令「產量」與 CropProduceApiView 重複
Ｘ 把指令改成「副產品」or「副產物」
Ｏ 維持「產量」，另外開發控制方式
'''

from .productcode import ProductCodeApiView
'''
reviewed
已開發完成待測試
'''
