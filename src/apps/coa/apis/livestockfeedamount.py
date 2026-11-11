from .configs import *


class LivestockFeedAmountApiView(ProductCityInquireApiView):
    """
    畜禽在養數量api介面

    - LivestockFeedAmount(在養數量)
        Builder: None
        Proxy: False
        Data:
            農業統計資料查詢 [農業生產統計]>>[畜禽飼養統計]>>[家畜飼養場數及頭數-按縣市別]、[家禽飼養場數及頭數-按縣市別]
            https://agrstat.moa.gov.tw/moasdweb/inquire/InquireAdvance.aspx?qcode=CD01
            https://agrstat.moa.gov.tw/moasdweb/inquire/InquireAdvance.aspx?qcode=CD02
    """
    tables = [
        ('CD01', '家畜別', '家畜飼養頭數'),
        ('CD02', '家禽別', '家禽飼養隻數'),
    ]
    label = '在養量'
    usage = '在養數量的指令為「在養量 畜禽 年份」或「在養量 畜禽 年份 縣市」，例如：\n「在養量 豬 113」\n「在養量 鴨 113 彰化」'
