from .configs import *


class LivestockFeedlotApiView(ProductCityInquireApiView):
    """
    畜禽飼養場數api介面

    - LivestockFeedlot(飼養場數)
        Builder: None
        Proxy: False
        Data:
            農業統計資料查詢 [農業生產統計]>>[畜禽飼養統計]>>[家畜飼養場數及頭數-按縣市別]、[家禽飼養場數及頭數-按縣市別]
            https://agrstat.moa.gov.tw/moasdweb/inquire/InquireAdvance.aspx?qcode=CD01
            https://agrstat.moa.gov.tw/moasdweb/inquire/InquireAdvance.aspx?qcode=CD02
    """
    tables = [
        ('CD01', '家畜別', '家畜飼養場數'),
        ('CD02', '家禽別', '家禽飼養場數'),
    ]
    label = '飼養場數'
    usage = '飼養場數的指令為「場數 畜禽 年份」或「場數 畜禽 年份 縣市」，例如：\n「場數 豬 113」\n「場數 鴨 113 彰化」'
