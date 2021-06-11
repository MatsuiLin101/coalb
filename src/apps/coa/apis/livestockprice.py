import os

from apps.coa.configs import ApiView
from apps.coa.utils import *


class LivestockPriceApiView(ApiView):
    '''
    畜禽價格api介面
    -price(價格)
    --毛豬
    ---交易價
    ---拍賣價
    ---平均重量價
    畜產行情資訊網 http://ppg.naif.org.tw/naif/MarketInformation/Pig/twStatistics.aspx
    --其他畜禽
    ---交易價
    ---拍賣價
    ---零售價
    畜產品價格查詢系統 http://price.naif.org.tw/Query/Query_now.aspx
    '''
