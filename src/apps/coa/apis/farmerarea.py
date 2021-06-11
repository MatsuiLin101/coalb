import os

from apps.coa.configs import ApiView
from apps.coa.utils import *


class FarmerAreaApiView(ApiView):
    '''
    耕地面積api介面
    farmerarea(耕地面積)
    年報八、(一)、2
    https://agrstat.coa.gov.tw/sdweb/public/book/Book.aspx
    '''
    def __init__(self, selfyear):
        super()
        self.url = "https://agrstat.coa.gov.tw/sdweb/public/book/Book.aspx"
        self.id_book = "ctl00_cphMain_uctlBook_grdBook_ctl10_btnBookName"
        self.id_ods = "ctl00_cphMain_uctlBook_repChapter_ctl52_dtlFile_ctl00_lnkFile"
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
            self.message = f"搜尋「耕地面積 {self.selfyear}」發生錯誤"
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
        self.message = f"「耕地面積 {self.selfyear}」年份必需在{list_years[0]}~{list_years[-1]}之間"

    def get_data(self):
        data_farmerarea = round(self.ws[f"D{self.row}"].value)
        self.message = f"搜尋「耕地面積 {self.selfyear}」的結果為：\n" + f"耕地面積：{data_farmerarea}(公頃)\n"
