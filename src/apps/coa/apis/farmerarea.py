from .configs import *


class FarmerAreaApiView(AnnualReportBasicApiView):
    """
    耕地面積api介面

    - FarmerArea(耕地面積)
        Builder: None
        Proxy: False
        Data:
            年報
            八、農業土地及自然環境
            (一)農業土地
            2農耕土地面積
            https://agrstat.moa.gov.tw/sdweb/public/book/Book.aspx
    """
    def __init__(self, params):
        super(FarmerAreaApiView, self).__init__(params)
        self.id_ods = 'ctl00_cphMain_uctlBook_repChapter_ctl51_dtlFile_ctl00_lnkFile'

        if len(params) != 2:
            raise CustomError('耕地面積的指令為「耕地面積 年份」，例如：\n「耕地面積 110」')

        self.command = params[0]
        self.query_date = params[1]

    def get_data(self):
        data_farmerarea = round(self.ws[f'D{self.row}'].value)

        self.message = f'{self.year}年 耕地面積：{data_farmerarea:,d}(公頃)'
        self.message += f'\n\n資料來源：{self.source}'
