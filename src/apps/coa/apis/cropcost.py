from .configs import *


class CropCostApiView(ApiView):
    '''
    農耕生產成本api介面
    -cost(生產成本)
    —-生產費用
    動態查詢 [農業生產統計]>>[農產品生產量值統計]>> [農產品每公頃生產費用：每公頃生產費用×生產費用與收益_農產品項目]>>[生產費用總計]
    https://agrstat.coa.gov.tw/sdweb/public/inquiry/InquireAdvance.aspx
    —-粗收益
    動態查詢 [農業生產統計]>>[農產品生產量值統計]>>  [農產品每公頃生產量與收益：每公頃生產量與收益×生產費用與收益_農產品項目]>>[粗收益]
    https://agrstat.coa.gov.tw/sdweb/public/inquiry/InquireAdvance.aspx
    —-淨收入率
    動態查詢
    https://agrstat.coa.gov.tw/sdweb/public/inquiry/InquireAdvance.aspx
    —-工時
    動態查詢 [農業生產統計]>>[農產品生產量值統計]>>[農產品每公頃人工時數(小時)：人工時數×生產費用與收益_農產品項目]>>[男工＋女工]合計
    https://agrstat.coa.gov.tw/sdweb/public/inquiry/InquireAdvance.aspx
    '''
