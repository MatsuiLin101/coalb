from .configs import *


class DisasterApiView(BasicApiView):
    '''
    災害api介面
    disaster(災害)
    年報十、1
    https://agrstat.coa.gov.tw/sdweb/public/book/Book.aspx
    '''
    def __init__(self, selfyear):
        super()
        self.url = "https://agrstat.coa.gov.tw/sdweb/public/book/Book.aspx"
        self.id_book = "ctl00_cphMain_uctlBook_grdBook_ctl10_btnBookName"
        self.id_ods = "ctl00_cphMain_uctlBook_repChapter_ctl77_dtlFile_ctl00_lnkFile"
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
            self.message = f"搜尋「災害 {self.selfyear}」發生錯誤"
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
        self.message = f"「災害 {self.selfyear}」年份必需在{list_years[0]}~{list_years[-1]}之間"

    def get_data(self):
        data_total = round(self.ws[f"D{self.row}"].value)
        data_sub = round(self.ws[f"E{self.row}"].value)
        data_crop = round(self.ws[f"F{self.row}"].value)
        data_livestock = round(self.ws[f"G{self.row}"].value)
        data_seafood = round(self.ws[f"H{self.row}"].value)
        data_wood = round(self.ws[f"I{self.row}"].value)
        data_facility = round(self.ws[f"K{self.row}"].value)
        self.message = f"搜尋「災害 {self.selfyear}」的結果為：\n" + f"合計：{int(data_total):,d}(千元)\n" + f"產物損失-小計：{int(data_sub):,d}(千元)\n" + f"產物損失-農作物：{int(data_crop):,d}(千元)\n" + f"產物損失-畜禽：{int(data_livestock):,d}(千元)\n" + f"產物損失-漁產：{int(data_seafood):,d}(千元)\n" + f"產物損失-林產：{int(data_wood):,d}(千元)\n" + f"民間設施損失-小計：{int(data_facility):,d}(千元)\n"
