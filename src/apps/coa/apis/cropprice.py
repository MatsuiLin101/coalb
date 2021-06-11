from .configs import *


class CropPriceApiView(ApiView):
    '''
    農耕價格api介面
    -price(價格)
    -—產地價
    農糧署農產品產地價格查報系統
    https://apis.afa.gov.tw/pagepub/AppContentPage.aspx?itemNo=PRI105
    —-批發價
    動態查詢 [農產品運銷統計]>>[農產品價格統計]>>[蔬菜批發價格：蔬菜別]、[果品批發價格：果品別]、[白米批發(躉售)價格：稻種別]
    https://agrstat.coa.gov.tw/sdweb/public/inquiry/InquireAdvance.aspx
    '''
