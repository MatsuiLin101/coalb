from .configs import *


class DisasterApiView(AnnualReportBasicApiView):
    """
    災害api介面

    - Disaster(災害)
        年報
        十、農業災害
        1農業災害產物及民間設施估計損失
        https://agrstat.moa.gov.tw/sdweb/public/book/Book.aspx
    """
    def __init__(self, params):
        super(DisasterApiView, self).__init__(params)
        self.id_ods = 'ctl00_cphMain_uctlBook_repChapter_ctl76_dtlFile_ctl00_lnkFile'

        if len(params) != 2:
            raise CustomError('災害的指令為「災害 年份」，例如：\n「災害 110」')

        self.command = params[0]
        self.query_date = params[1]

    def get_data(self):
        data_total = round(self.ws[f'D{self.row}'].value)
        data_sub = round(self.ws[f'E{self.row}'].value)
        data_crop = round(self.ws[f'F{self.row}'].value)
        data_livestock = round(self.ws[f'G{self.row}'].value)
        data_seafood = round(self.ws[f'H{self.row}'].value)
        data_wood = round(self.ws[f'I{self.row}'].value)
        data_facility = round(self.ws[f'K{self.row}'].value)

        self.message = f'{self.year}年 災害：\n'
        self.message += f'合計：{int(data_total):,d}(千元)\n'
        self.message += f'產物損失-小計：{int(data_sub):,d}(千元)\n'
        self.message += f'產物損失-農作物：{int(data_crop):,d}(千元)\n'
        self.message += f'產物損失-畜禽：{int(data_livestock):,d}(千元)\n'
        self.message += f'產物損失-漁產：{int(data_seafood):,d}(千元)\n'
        self.message += f'產物損失-林產：{int(data_wood):,d}(千元)\n'
        self.message += f'民間設施損失-小計：{int(data_facility):,d}(千元)'
        self.message += f'\n\n資料來源：{self.source}'
