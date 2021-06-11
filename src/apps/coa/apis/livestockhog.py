from .configs import *


class LivestockHogApiView(ApiView):
    '''
    毛豬價格api介面
    -交易量
    -拍賣價
    -平均重量
    畜產行情資訊網 http://ppg.naif.org.tw/naif/MarketInformation/Pig/twStatistics.aspx
    '''
