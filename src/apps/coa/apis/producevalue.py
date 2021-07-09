from .configs import *


class ProduceValueApiView(BasicApiView):
    '''
    產值api介面
    producevalue(產值)
    -TotalValue(總產值)
    動態查詢 [農業生產統計]>>[農業產值結構與指標]>>[農業產值：縣市別×農業別]
    https://agrstat.coa.gov.tw/sdweb/public/inquiry/InquireAdvance.aspx
    -Value(產值)
    年報一、(四)
    https://agrstat.coa.gov.tw/sdweb/public/book/Book.aspx
    '''
    def __init__(self, params):
        self.params = params
        self.command = params[0]

    def choose_api(self):
        if self.command in ["產值"]:
            return ValueApiView(self.params)


class TotalValueApiView(BasicApiView):
    '''
    producevalue(產值)
    -TotalValue(總產值)
    動態查詢 [農業生產統計]>>[農業產值結構與指標]>>[農業產值：縣市別×農業別]
    https://agrstat.coa.gov.tw/sdweb/public/inquiry/InquireAdvance.aspx
    '''
    def __init__(self, params):
        self.driver = None
        self.url = "https://agrstat.coa.gov.tw/sdweb/public/inquiry/InquireAdvance.aspx"
        self.text_title = "農業產值結構與指標"
        self.text_group = "農業產值：縣市別×農業別"
        self.id_group = "ctl00_cphMain_uctlInquireAdvance_lstFieldGroup"
        self.id_city = "ctl00_cphMain_uctlInquireAdvance_dtlDimension_ctl00_lstDimension"
        self.id_category = "ctl00_cphMain_uctlInquireAdvance_dtlDimension_ctl02_lstDimension"
        self.id_search = "ctl00_cphMain_uctlInquireAdvance_btnQuery"
        self.id_start = "ctl00_cphMain_uctlInquireAdvance_ddlYearBegin"
        self.id_end = "ctl00_cphMain_uctlInquireAdvance_ddlYearEnd"
        self.id_query = "ctl00_cphMain_uctlInquireAdvance_btnQuery2"
        self.id_table = "ctl00_cphMain_uctlInquireAdvance_tabResult"
        self.id_back = "ctl00_cphMain_uctlInquireAdvance_btnBack2"
        self.message = ""



class ValueApiView(AnnualReportBasicApiView):
    '''
    -Value(產值)
    年報一、(四)
    https://agrstat.coa.gov.tw/sdweb/public/book/Book.aspx
    '''
    def __init__(self, params):
        super(ValueApiView, self).__init__(params)
        self.id_ods = "ctl00_cphMain_uctlBook_repChapter_ctl06_dtlFile_ctl00_lnkFile"

        if not len(params) == 3:
            raise CustomError(f"產值的指令為「產值 品項 年份」，例如：\n「產值 豬 108」")
        self.command = params[0]
        self.product = params[1]
        self.query_date = params[2]

    def open_wb(self):
        # open value xslx
        wb = load_workbook(filename=self.xlsx_name)
        self.list_ws = [wb[sheetname] for sheetname in wb.sheetnames]

    def verify_date(self):
        # verify query year
        try:
            self.year = int(self.query_date)
        except Exception as e:
            self.message = f"年份「{self.query_date}」無效，請輸入民國年"
            raise CustomError(self.message)

        ws = self.list_ws[0]
        list_years = [ws['G5'], ws['K5'], ws['P5'], ws['T5']]
        if not any(str(self.year) in year.value for year in list_years):
            self.message = f"「{self.command_text}」年份必須符合以下：\n" + "\n".join(year.value for year in list_years)
            raise CustomError(self.message)
        else:
            match_year = [year for year in list_years if str(self.year) in year.value][0]
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
            self.message = "\n".join(f"{self.year}年 {result[0]} 產值：{round(result[1]):,d}(千元)" for result in list_result)
        else:
            self.message = f"{self.year}年 {self.product} 產值：查無資料"
