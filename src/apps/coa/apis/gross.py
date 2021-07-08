from .configs import *


class GrossApiView(AnnualReportBasicApiView):
    '''
    國內生產毛額api介面
    gross(國內生產毛額)
    年報一、(一)
    https://agrstat.coa.gov.tw/sdweb/public/book/Book.aspx
    '''
    def __init__(self, params):
        super(GrossApiView, self).__init__(params)
        self.id_ods = "ctl00_cphMain_uctlBook_repChapter_ctl03_dtlFile_ctl00_lnkFile"

        if not len(params) == 2:
            raise CustomError(f"生產毛額的指令為「生產毛額 年份」，例如：\n「生產毛額 107」")
        self.command = params[0]
        self.query_date = params[1]

    def get_data(self):
        data_total = self.ws[f"D{self.row}"].value
        data_farm = self.ws[f"F{self.row}"].value
        data_factor = self.ws[f"H{self.row}"].value
        data_service = self.ws[f"K{self.row}"].value
        self.message = f"搜尋「生產毛額 {self.selfyear}」的結果為：\n" + f"合計：{data_total}(百萬元)\n" + f"農業：{data_farm}(百萬元)\n" + f"工業：{data_factor}(百萬元)\n" + f"服務業：{data_service}(百萬元)\n"
