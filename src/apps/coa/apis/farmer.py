from .configs import *


class FarmerApiView(AnnualReportBasicApiView):
    '''
    農家(農牧戶)api介面
    farmer(農家(農牧戶))
    年報五、1
    https://agrstat.coa.gov.tw/sdweb/public/book/Book.aspx
    '''
    def __init__(self, params):
        super(FarmerApiView, self).__init__(params)
        self.id_ods = "ctl00_cphMain_uctlBook_repChapter_ctl28_dtlFile_ctl00_lnkFile"

        if not len(params) == 2:
            raise CustomError(f"農牧戶戶數/人口數的指令為「農牧戶 年份」，例如：\n「農牧戶 106」")
        self.command = params[0]
        self.query_date = params[1]

    def get_data(self):
        data_person = round(self.ws[f"G{self.row}"].value)
        data_family = round(self.ws[f"F{self.row}"].value)
        self.message = f"{self.year}年 農牧戶 人口數：{data_person:,d}(人)\n" + f"{self.year}年 農牧戶 戶數：{data_family:,d}(戶)\n\n" + f"資料來源：{self.source}"
