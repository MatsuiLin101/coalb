from .configs import *


class LivestockFeedlotApiView(ApiView):
    '''
    畜禽飼養場數api介面
    -feedlot(飼養場數)
    動態查詢 [農業生產統計]>>[畜禽產品飼養數量統計]>>[家畜飼養場數]、[家禽飼養場數：縣市別×家禽別(104年起)]
    https://agrstat.coa.gov.tw/sdweb/public/inquiry/InquireAdvance.aspx
    '''
