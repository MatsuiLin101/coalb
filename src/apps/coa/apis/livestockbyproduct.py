import os

from apps.coa.configs import ApiView
from apps.coa.utils import *


class LivestockByproductApiView(ApiView):
    '''
    畜禽副產物供應量api介面
    -byproduct(副產物產量)
    動態查詢 [農業生產統計]>>[畜禽產品生產量值統計]>> [畜禽副產品產量]、[蜂蠶飼養產量]
    https://agrstat.coa.gov.tw/sdweb/public/inquiry/InquireAdvance.aspx
    '''
