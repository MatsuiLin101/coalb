from .configs import *


class LaborforceApiView(BasicApiView):
    '''
    勞動力(就業人口)api介面
    laborforce(勞動力)
    動態查詢 [勞工統計]>>[勞動力統計]>>[農業就業人口]
    https://agrstat.moa.gov.tw/sdweb/public/inquiry/InquireAdvance.aspx
    '''
    def __init__(self, params):
        self.driver = None
        self.url = "https://agrstat.moa.gov.tw/sdweb/public/inquiry/InquireAdvance.aspx"
        self.text_title = "勞動力統計"
        self.text_group = "農業就業人口"
        self.id_group = "ctl00_cphMain_uctlInquireAdvance_lstFieldGroup"
        self.id_search = "ctl00_cphMain_uctlInquireAdvance_btnQuery"
        self.id_check_year = "ctl00_cphMain_uctlInquireAdvance_chkYear"
        self.id_start_year = "ctl00_cphMain_uctlInquireAdvance_ddlYearBegin"
        self.id_end_year = "ctl00_cphMain_uctlInquireAdvance_ddlYearEnd"
        self.id_check_month = "ctl00_cphMain_uctlInquireAdvance_chkMonth"
        self.id_start_month = "ctl00_cphMain_uctlInquireAdvance_ddlMonthBegin"
        self.id_end_month = "ctl00_cphMain_uctlInquireAdvance_ddlMonthEnd"
        self.id_query = "ctl00_cphMain_uctlInquireAdvance_btnQuery2"
        self.id_table = "ctl00_cphMain_uctlInquireAdvance_tabResult"
        self.message = ""
        self.year = ""
        self.month = ""

        if not len(params) == 2:
            raise CustomError(f"就業人口的指令為「就業人口 年份」或「就業人口 年份/月份」，例如：\n「就業人口 108」\n「就業人口 109/3」")
        self.command = params[0]
        self.query_date = params[1]
        self.command_text = " ".join(text for text in params)

    def verify_date(self):
        # 檢查年份是否為數字
        if '/' in self.query_date:
            self.year, self.month = self.query_date.split('/')
        else:
            self.year = self.query_date
        try:
            self.year = int(self.year)
        except Exception as e:
            self.message = f"年份「{self.year}」無效，請輸入民國年"
            raise CustomError(self.message)
        # 檢查月份是否為數字
        if self.month:
            try:
                self.month = int(self.month)
            except Exception as e:
                self.message = f"月份「{self.month}」無效，請輸入1～12"
                raise CustomError(self.message)
        self.select_value = f"{str(self.year).zfill(3)}{str(self.month).zfill(2)}" if self.month else f"{str(self.year).zfill(3)}"

    def parser(self):
        super(LaborforceApiView, self).parser()
        # 進入勞動力統計頁面
        self.driver.find_element(By.LINK_TEXT, self.text_title).click()
        driver_select(self.driver, self.id_group, "text", self.text_group)
        btn_search = self.driver.find_element(By.ID, self.id_search)
        btn_search.click()

    def get_table(self):
        if self.month:
            check_select = self.driver.find_element(By.ID, self.id_check_year)
            select_start = self.id_start_month
            select_end = self.id_end_month
        else:
            check_select = self.driver.find_element(By.ID, self.id_check_month)
            select_start = self.id_start_year
            select_end = self.id_end_year

        check_select.click()
        try:
            driver_select(self.driver, select_start, "value", self.select_value)
            driver_select(self.driver, select_end, "value", self.select_value)
        except Exception as e:
            options = self.driver.find_element(By.ID, select_start).text.replace(" ", "").replace("月", "")
            if self.month:
                options = options.replace("年", "/")
            else:
                options = options.replace("年", "")
            options = options.split("\n")
            date_start = options[0]
            date_end = options[-1]
            self.message = f"日期「{self.query_date}」無效，日期需介於「{date_start}」～「{date_end}」之間"
            raise CustomError(self.message)
        btn_query = self.driver.find_element(By.ID, self.id_query)
        btn_query.click()

    def get_result(self):
        WebDriverWait(self.driver, 30, 0.1).until(EC.presence_of_element_located((By.ID, self.id_table)))
        table = self.driver.find_element(By.ID, self.id_table)
        self.unit = table.find_element(By.CSS_SELECTOR, ".HorDim").text.split("人口")[-1]
        self.result = self.driver.find_element(By.CSS_SELECTOR, ".VerDim").parent.find_element(By.CSS_SELECTOR, ".ValueLeftTop").text

    def get_data(self):
        self.parser()
        self.get_table()
        self.get_result()
        if self.month:
            self.message = f"{self.year}年{self.month}月 就業人口：{self.result}{self.unit}"
        else:
            self.message = f"{self.year}年 就業人口：{self.result}{self.unit}"
