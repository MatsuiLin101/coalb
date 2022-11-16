"""
coa.apis package
"""

from .producevalue import ProduceValueApiView
'''
資料來源：動態查詢、年報

指令(choose)
-總產值
-產值

已修正
總產值修改縣市查詢規則，有完全符合的就不檢查其他選項
台南市
台灣省台南市
'''

from .gross import GrossApiView
'''
資料來源：年報

指令
-毛額
-生產毛額
'''

from .income import IncomeApiView
'''
資料來源：年報

指令
-所得
-農家所得
'''

from .farmer import FarmerApiView
'''
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
資料來源：年報

指令
-耕地面積
'''

from .laborforce import LaborforceApiView
'''
資料來源：動態查詢

指令
-勞動力
-就業人口
'''

from .disaster import DisasterApiView
'''
資料來源：年報

指令
-災害
'''

from .welfare import WelfareApiView
'''
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

from .cropprice import CropPriceApiView, CropPriceOriginApiView
'''
資料來源：產地價查報、動態查詢

指令(choose)
-產地
-批發

已修正
產地價 - 部署後無法使用需要除錯
- 網站似乎有限制台灣ip才能訪問，設定產地價api會特別使用proxy(需事先設定，失效需要更換)
Taiwan proxy
http://free-proxy.cz/zh/proxylist/country/TW/all/ping/all
1.2.3.4:5678
'''

from .cropproduce import CropProduceApiView
'''
資料來源：農情報告、匯入

指令(choose)
-產量
-種植面積
-單位產值
-單位產量

已完成
合併「產量」「種植面積」指令
合併「單位產值」「單位產量」指令
與副產物產量(LivestockByproductApiView)共用「產量」指令
「產量」「種植面積」 - 作物太多查詢時間過長會導致reply_token失效(30秒)
-限制查詢作物不可超過5個

2022/11/14 網站限制海外IP，改用proxy取得資料

待修正
透過line上傳檔案(單位產值、單位產量excel)會因為檔案太大處理時間超過30秒，導致上傳者無法取得機器人回應，可以開發一個檔案上傳頁面取代透過line上傳檔案
'''

from .cropcost import CropCostApiView
'''
資料來源：動態查詢

指令(choos)
-成本、生產成本
-費用、生產費用
-粗收益
-淨收入率
-工時
'''

from .livestockhog import LivestockHogApiView
'''
資料來源：畜產行情

指令
-毛豬
-交易量
-價格
-重量

已修改
更改指令統一為「毛豬」
保留「交易量」、「價格」、「重量」指令
'''

from .livestockprice import LivestockPriceApiView
'''
資料來源：畜產查詢

指令(choose)
-拍賣價
-產地價
-零售價

待開發
控制查詢品項數量避免查詢時間過長無法回應

已修正
部署後無法使用需要除錯
-切換選單速度過快會導致新內容還沒出現爬蟲就先抓取，抓不到內容報錯
'''

from .livestockfeedlot import LivestockFeedlotApiView
'''
資料來源：動態查詢

指令
-場數
-飼養場數
'''

from .livestockfeedamount import LivestockFeedamountApiView
'''
資料來源：動態查詢

指令
-在養
-在養量
'''

from .livestockslaughter import LivestockSlaughterApiView
'''
資料來源：動態查詢

指令
-屠宰
-屠宰量
'''

from .livestockbyproduct import LivestockByproductApiView
'''
資料來源：動態查詢

指令
-副產
-副產品
-副產物

已完成
與作物產量(CropProduceApiView)共用「產量」指令
保留「副產物」「副產品」指令
'''

from .productcode import ProductCodeApiView
'''
資料來源：匯入

指令
-代碼
-作物代碼
'''
