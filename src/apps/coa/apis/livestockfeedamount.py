from .configs import *


class LivestockFeedamountApiView(ApiView):
    '''
    畜禽在養數量api介面
    -feedamount(在養數量)
    動態查詢 [農業生產統計]>>[畜禽產品飼養數量統計]>>[家畜飼養頭數]、[家禽飼養隻數：縣市別×家禽別(104年起)]
    https://agrstat.coa.gov.tw/sdweb/public/inquiry/InquireAdvance.aspx
    '''
