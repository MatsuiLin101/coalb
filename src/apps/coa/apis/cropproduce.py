import os

from apps.coa.configs import ApiView
from apps.coa.utils import *


class CropProduceApiView(ApiView):
    '''
    農耕作物生產api介面
    -produce(作物生產)
    --(NEW)產量
    農糧署農情報告資源網 https://agr.afa.gov.tw/afa/afa_frame.jsp
    --(NEW)種植面積
    農糧署農情報告資源網 https://agr.afa.gov.tw/afa/afa_frame.jsp
    —-單位產值
    EXCEL匯入
    —-單位產量
    EXCEL匯入
    '''
