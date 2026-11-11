from .configs import *


class LivestockSlaughterApiView(ProductCityInquireApiView):
    """
    畜禽供應屠宰量api介面

    - LivestockSlaughter(供應屠宰量)
        Builder: None
        Proxy: False
        Data:
            農業統計資料查詢 [農業生產統計]>>[畜禽產品生產量值統計]>>[家畜供應屠宰頭數及體重-按縣市別]、[家禽供應屠宰頭數及體重-按縣市別]
            https://agrstat.moa.gov.tw/moasdweb/inquire/InquireAdvance.aspx?qcode=CE05
            https://agrstat.moa.gov.tw/moasdweb/inquire/InquireAdvance.aspx?qcode=CE06
    """
    tables = [
        ('CE05', '家畜別', '家畜供應屠宰頭數'),
        ('CE06', '家禽別', '家禽供應屠宰隻數'),
    ]
    label = '供應屠宰量'
    usage = '供應屠宰量的指令為「屠宰 畜禽 年份」或「屠宰 畜禽 年份 縣市」，例如：\n「屠宰 豬 113」\n「屠宰 鴨 113 彰化」'
