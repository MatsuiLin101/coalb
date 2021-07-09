"""
coa.apis package
"""

from .value import ValueApiView
'''
資料來源：動態查詢、年報

指令(choose)
-總產值
-產值

總產值修改縣市查詢規則，有完全符合的就不檢查其他選項
台南市
台灣省台南市
'''

from .gross import GrossApiView
'''
reviewed
資料來源：年報

指令
-毛額
-生產毛額
'''

from .income import IncomeApiView
'''
reviewed
資料來源：年報

指令
-所得
-農家所得
'''

from .farmer import FarmerApiView
'''
reviewed
資料來源：年報

指令
-農牧戶
-農牧戶人口數
-農牧戶戶數
-人口數
-戶數
'''

from .farmerarea import FarmerAreaApiView
'''
reviewed
資料來源：年報

指令
-耕地面積
'''

from .laborforce import LaborforceApiView
'''
reviewed
資料來源：動態查詢

指令
-勞動力
-就業人口
'''

from .disaster import DisasterApiView
'''
reviewed
資料來源：年報

指令
-災害
'''

from .welfare import WelfareApiView
'''
reviewed
資料來源：動態查詢

指令(choose)
-農保
-津貼、老農津貼
-獎助學金

已修正
Scholarship無法查詢到縣市
獎助學金沒有提供縣市月份資料，應該是有帶月份才會查詢不到

待優化
改善縣市查詢方式
'''

from .cropprice import CropPriceApiView
'''
資料來源：產地價查報、動態查詢

指令(choose)
-產地
-批發

已開發完成待測試

待修正
產地價 - 部署後無法使用需要除錯
'''

from .cropproduce import CropProduceApiView
'''
資料來源：農情報告、匯入

指令(choose)
-產量
-種植面積
-單位產值
-單位產量

已開發完成待測試

待開發
合併「產量」「種植面積」指令
合併「單位產值」「單位產量」指令

待修正
「產量」「種植面積」 - 作物太多查詢時間過長會導致reply_token失效(30秒)
'''

from .cropcost import CropCostApiView
'''
reviewed
資料來源：動態查詢

指令(choos)
-成本、生產成本
-費用、生產費用
-粗收益
-淨收入率
-工時

已開發完成待測試
'''

from .livestockhog import LivestockHogApiView
'''
資料來源：畜產行情

指令
-毛豬
-交易量
-價格
-重量

待開發
更改指令統一為「毛豬」
'''

from .livestockprice import LivestockPriceApiView
'''
資料來源：畜產查詢

指令(choose)
-拍賣價
-產地價
-零售價

已開發完成待測試

待修正
部署後無法使用需要除錯
'''

from .livestockfeedlot import LivestockFeedlotApiView
'''
reviewed
資料來源：動態查詢

指令
-場數
-飼養場數

已開發完成待測試
'''

from .livestockfeedamount import LivestockFeedamountApiView
'''
reviewed
資料來源：動態查詢

指令
-在養
-在養量

已開發完成待測試
'''

from .livestockslaughter import LivestockSlaughterApiView
'''
reviewed
資料來源：動態查詢

指令
-屠宰
-屠宰量

已開發完成待測試
'''

from .livestockbyproduct import LivestockByproductApiView
'''
資料來源：動態查詢

指令
-副產
-副產品
-副產物

已開發完成待測試

待開發
原指令「產量」與 CropProduceApiView 重複
Ｘ 把指令改成「副產品」or「副產物」
Ｏ 維持「產量」，另外開發控制方式
'''

from .productcode import ProductCodeApiView
'''
reviewed
資料來源：匯入

指令
-代碼
-作物代碼


已開發完成待測試
'''
