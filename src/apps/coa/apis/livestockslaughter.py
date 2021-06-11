import os

from apps.coa.configs import ApiView
from apps.coa.utils import *


class LivestockSlaughterApiView(ApiView):
    '''
    畜禽供應屠宰量api介面
    -slaughter(供應屠宰量)
    動態查詢 [農業生產統計]>>[畜禽產品生產量值統計]>> [家畜供應屠宰頭數]、[家禽供應屠宰隻數]
    https://agrstat.coa.gov.tw/sdweb/public/inquiry/InquireAdvance.aspx
    '''
