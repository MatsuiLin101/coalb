from .configs import *


class FarmerApiView(AnnualReportBasicApiView):
    """
    農家(農牧戶)api介面

    - Farmer(農家(農牧戶))
        五、農家與農家經濟
        1臺灣地區總戶口與農牧戶
        https://agrstat.moa.gov.tw/sdweb/public/book/Book.aspx
    """
    def __init__(self, params):
        super(FarmerApiView, self).__init__(params)
        self.id_ods = 'ctl00_cphMain_uctlBook_repChapter_ctl27_dtlFile_ctl00_lnkFile'

        if len(params) != 2:
            raise CustomError('農牧戶戶數/人口數的指令為「農牧戶 年份」，例如：\n「農牧戶 110」')

        self.command = params[0]
        self.query_date = params[1]

    def get_data(self):
        data_person = round(self.ws[f'G{self.row}'].value)
        data_family = round(self.ws[f'F{self.row}'].value)

        self.message = f'{self.year}年 農牧戶 人口數：{data_person:,d}(人)\n'
        self.message += f'{self.year}年 農牧戶 戶數：{data_family:,d}(戶)'
        self.message += f'\n\n資料來源：{self.source}'
