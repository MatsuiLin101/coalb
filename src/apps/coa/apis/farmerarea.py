from .configs import *


class FarmerAreaApiView(AnnualReportBasicApiView):
    '''
    耕地面積api介面
    farmerarea(耕地面積)
    年報八、(一)、2
    https://agrstat.moa.gov.tw/sdweb/public/book/Book.aspx
    '''
    def __init__(self, params):
        super(FarmerAreaApiView, self).__init__(params)
        self.id_ods = "ctl00_cphMain_uctlBook_repChapter_ctl52_dtlFile_ctl00_lnkFile"

        if not len(params) == 2:
            raise CustomError(f"耕地面積的指令為「耕地面積 年份」，例如：\n「耕地面積 106」")
        self.command = params[0]
        self.query_date = params[1]

    def get_data(self):
        data_farmerarea = round(self.ws[f"D{self.row}"].value)
        self.message = f"{self.year}年 耕地面積：{data_farmerarea:,d}(公頃)\n\n" + f"資料來源：{self.source}"
