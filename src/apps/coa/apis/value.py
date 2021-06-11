from .configs import *


class ValueApiView(ApiView):
    '''
    產值api介面
    value(產值)
    -總產值
    動態查詢 [農業生產統計]>>[農業產值結構與指標]>>[農業產值：縣市別×農業別]
    https://agrstat.coa.gov.tw/sdweb/public/inquiry/InquireAdvance.aspx
    -產值
    年報一、(四)
    https://agrstat.coa.gov.tw/sdweb/public/book/Book.aspx
    '''
    def __init__(self, selfyear, product):
        super()
        self.url = "https://agrstat.coa.gov.tw/sdweb/public/book/Book.aspx"
        self.id_book = "ctl00_cphMain_uctlBook_grdBook_ctl10_btnBookName"
        self.id_ods = "ctl00_cphMain_uctlBook_repChapter_ctl06_dtlFile_ctl00_lnkFile"
        self.selfyear = str(selfyear)
        self.product = str(product)
        self.xlsx_name = ""
        self.message = ""

    def api(self):
        try:
            self.download()
            self.open_wb()
            self.check_year()
            if not self.message:
                self.get_data()
        except Exception as e:
            self.message = f"搜尋「產值 {self.selfyear} {self.product}」發生錯誤"
        os.remove(self.xlsx_name) if self.xlsx_name else None
        return self.message

    def open_wb(self):
        # open value xslx
        wb = load_workbook(filename=self.xlsx_name)
        self.list_ws = [wb[sheetname] for sheetname in wb.sheetnames]

    def check_year(self):
        # check years
        ws = self.list_ws[0]
        list_years = [ws['G5'], ws['K5'], ws['P5'], ws['T5']]
        if not any(self.selfyear in year.value for year in list_years):
            self.message = f"「產值 {self.selfyear} {self.product}」年份必須符合以下：\n" + "\n".join(year.value for year in list_years)
        else:
            match_year = [year for year in list_years if self.selfyear in year.value][0]
            col_year = match_year.col_idx
            self.col_value = col_year - 1 + 2

    def get_data(self):
        # search product
        list_result = list()
        for ws in self.list_ws:
            for row in ws.rows:
                if row[0].row <= 13:
                    continue
                if row[3].value is not None and self.product in row[3].value:
                    value = row[self.col_value].value
                    list_result.append((row[3].value, value))
        if list_result:
            self.message = f"搜尋「產值 {self.selfyear} {self.product}」的結果為：\n" + "\n".join(f"{result[0]} {round(result[1])}" for result in list_result)
        else:
            self.message = f"「產值 {self.selfyear} {self.product}」查無資料。"
