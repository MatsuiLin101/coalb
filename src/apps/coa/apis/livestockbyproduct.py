from .configs import *


class LivestockByproductApiView(ProductCityInquireApiView):
    """
    畜禽副產物產量api介面

    - LivestockByproduct(副產物產量)
        Builder: None
        Proxy: False
        Data:
            農業統計資料查詢 [農業生產統計]>>[畜禽產品生產量值統計]>>[畜禽副產品產量-按縣市別]、[蜂蠶飼養產量及產值-按縣市別]
            https://agrstat.moa.gov.tw/moasdweb/inquire/InquireAdvance.aspx?qcode=CE03
            https://agrstat.moa.gov.tw/moasdweb/inquire/InquireAdvance.aspx?qcode=CE04
    """
    tables = [
        ('CE03', '畜禽副產品別', '畜禽副產品產量'),
        ('CE04', '特飼及其產品別', '蜂蠶飼養產量'),
    ]
    # 「產量」指令與作物產量共用，views 依這份清單判斷是不是副產物
    products = ['牛乳', '羊乳', '鹿茸', '生皮', '雞蛋', '鴨蛋', '蜂蜜', '蜂王漿', '蜂蠟', '蠶']
    label = '產量'
    usage = '副產物的指令為「副產物 品項 年份」或「副產物 品項 年份 縣市」，例如：\n「副產物 蜂蜜 113」\n「副產物 蜂蜜 113 彰化」'

    @classmethod
    def is_product(cls, keyword):
        keyword = keyword.replace('台', '臺')
        return any(keyword in product or product in keyword for product in cls.products)
