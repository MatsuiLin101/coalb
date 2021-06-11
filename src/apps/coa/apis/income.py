from .configs import *


class IncomeApiView(ApiView):
    '''
    所得api介面
    income(所得)
    年報五、3
    https://agrstat.coa.gov.tw/sdweb/public/book/Book.aspx
    '''
    def __init__(self, selfyear):
        super()
        self.url = "https://agrstat.coa.gov.tw/sdweb/public/book/Book.aspx"
        self.id_book = "ctl00_cphMain_uctlBook_grdBook_ctl10_btnBookName"
        self.id_ods = "ctl00_cphMain_uctlBook_repChapter_ctl30_dtlFile_ctl00_lnkFile"
        self.selfyear = str(selfyear)
        self.xlsx_name = ""
        self.message = ""
        self.row = ""

    def api(self):
        try:
            self.download()
            self.open_wb()
            self.check_year()
            if not self.message:
                self.get_data()
        except Exception as e:
            self.message = f"搜尋「農家所得 {self.selfyear}」發生錯誤"
        os.remove(self.xlsx_name) if self.xlsx_name else None
        return self.message

    def open_wb(self):
        # open value xslx
        wb = load_workbook(filename=self.xlsx_name)
        self.ws = wb[wb.sheetnames[0]]

    def check_year(self):
        # check years
        list_years = list()
        for row in self.ws.rows:
            year = row[1].value
            if year is not None:
                try:
                    int(year)
                    list_years.append(year)
                except Exception as e:
                    continue

                if self.selfyear == str(year):
                    self.row = row[0].row
                    return
        self.message = f"「農家所得 {self.selfyear}」年份必需在{list_years[0]}~{list_years[-1]}之間"

    def get_data(self):
        data_income = round(self.ws[f"F{self.row}"].value)
        data_farm_income = round(self.ws[f"G{self.row}"].value)
        data_main_income = round(self.ws[f"H{self.row}"].value)
        data_main_farm_income = round(self.ws[f"I{self.row}"].value)
        self.message = f"搜尋「農家所得 {self.selfyear}」的結果為：\n" + f"農家 所得：{data_income}(元)\n" + f"農家 農業所得：{data_farm_income}(元)\n" + f"主力農家 所得：{data_main_income}(元)\n" + f"主力農家 農業所得：{data_main_farm_income}(元)\n"
