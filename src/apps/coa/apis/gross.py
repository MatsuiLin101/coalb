from .configs import *


class GrossApiView(BasicApiView):
    '''
    國內生產毛額api介面
    gross(國內生產毛額)
    年報一、(一)
    https://agrstat.coa.gov.tw/sdweb/public/book/Book.aspx
    '''
    def __init__(self, selfyear):
        super()
        self.url = "https://agrstat.coa.gov.tw/sdweb/public/book/Book.aspx"
        self.id_book = "ctl00_cphMain_uctlBook_grdBook_ctl10_btnBookName"
        self.id_ods = "ctl00_cphMain_uctlBook_repChapter_ctl03_dtlFile_ctl00_lnkFile"
        self.selfyear = str(selfyear)
        self.xlsx_name = ""
        self.message = ""
        self.row = ""

    def execute_api(self):
        try:
            self.download()
            self.open_wb()
            self.check_year()
            if not self.message:
                self.get_data()
        except Exception as e:
            self.message = f"搜尋「生產毛額 {self.selfyear}」發生錯誤"
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
                list_years.append(year)
                if self.selfyear == str(year):
                    self.row = row[0].row
                    return
        self.message = f"「生產毛額 {self.selfyear}」年份必需在{list_years[0]}~{list_years[-1]}之間"

    def get_data(self):
        data_total = self.ws[f"D{self.row}"].value
        data_farm = self.ws[f"F{self.row}"].value
        data_factor = self.ws[f"H{self.row}"].value
        data_service = self.ws[f"K{self.row}"].value
        self.message = f"搜尋「生產毛額 {self.selfyear}」的結果為：\n" + f"合計：{data_total}(百萬元)\n" + f"農業：{data_farm}(百萬元)\n" + f"工業：{data_factor}(百萬元)\n" + f"服務業：{data_service}(百萬元)\n"
