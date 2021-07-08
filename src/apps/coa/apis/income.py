from .configs import *


class IncomeApiView(AnnualReportBasicApiView):
    '''
    所得api介面
    income(所得)
    年報五、3
    https://agrstat.coa.gov.tw/sdweb/public/book/Book.aspx
    '''
    def __init__(self, params):
        super(GrossApiView, self).__init__(params)
        self.id_ods = "ctl00_cphMain_uctlBook_repChapter_ctl30_dtlFile_ctl00_lnkFile"

        if not len(params) == 2:
            raise CustomError(f"農家所得的指令為「農家所得 年份」，例如：\n「農家所得 107」")
        self.command = params[0]
        self.query_date = params[1]

    def get_data(self):
        data_income = round(self.ws[f"F{self.row}"].value)
        data_farm_income = round(self.ws[f"G{self.row}"].value)
        data_main_income = round(self.ws[f"H{self.row}"].value)
        data_main_farm_income = round(self.ws[f"I{self.row}"].value)
        self.message = f"搜尋「農家所得 {self.selfyear}」的結果為：\n" + f"農家 所得：{data_income}(元)\n" + f"農家 農業所得：{data_farm_income}(元)\n" + f"主力農家 所得：{data_main_income}(元)\n" + f"主力農家 農業所得：{data_main_farm_income}(元)\n"
