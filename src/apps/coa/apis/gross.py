from .configs import *


class GrossApiView(AnnualReportBasicApiView):
    """
    國內生產毛額api介面

    - Gross(國內生產毛額)
        Builder: None
        Proxy: False
        Data:
            年報
            一、農業經濟指標
            (一)國內生產毛額與經濟成長率
            https://agrstat.moa.gov.tw/sdweb/public/book/Book.aspx
    """
    def __init__(self, params):
        super(GrossApiView, self).__init__(params)
        self.id_ods = 'ctl00_cphMain_uctlBook_repChapter_ctl03_dtlFile_ctl00_lnkFile'

        if len(params) != 2:
            raise CustomError('生產毛額的指令為「生產毛額 年份」，例如：\n「生產毛額 105」')

        self.command = params[0]
        self.query_date = params[1]

    def get_data(self):
        data_total = self.ws[f'D{self.row}'].value
        data_farm = self.ws[f'F{self.row}'].value
        data_factor = self.ws[f'H{self.row}'].value
        data_service = self.ws[f'K{self.row}'].value

        self.message = f'{self.year}年 國內生產毛額：\n'
        self.message += f'合計：{data_total:,d}(百萬元)\n'
        self.message += f'農業：{data_farm:,d}(百萬元)\n'
        self.message += f'工業：{data_factor:,d}(百萬元)\n'
        self.message += f'服務業：{data_service:,d}(百萬元)'
        self.message += f'\n\n資料來源：{self.source}'
