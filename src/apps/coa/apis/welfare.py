import os

from apps.coa.configs import ApiView
from apps.coa.utils import *


class WelfareApiView(ApiView):
    '''
    社會福利api介面
    農保
    老農津貼
    農漁民子女獎助學金
    '''
    def __init__(self, command, query_date, city=None):
        super()
        self.command = command
        self.query_date = str(query_date)
        self.city = city
        if city:
            self.city = city.replace("台", "臺")

    def chose_api(self):
        if self.command == "農保":
            return Insurance(self.command, self.query_date, self.city)
        elif self.command == "老農津貼":
            return Allowance(self.command, self.query_date, self.city)
        elif self.command == "獎助學金":
            return Scholarship(self.command, self.query_date, self.city)

    def api(self):
        try:
            self.check_year()
            if not self.message:
                self.get_data()
        except Exception as e:
            if not self.message:
                self.message = f"搜尋「{self.command} {self.selfyear}」發生錯誤"
        if self.driver:
            self.driver.close()
        return self.message

    def check_year(self):
        # check years
        # 檢查年份是否為數字
        try:
            int(self.selfyear)
        except Exception as e:
            self.message = f"年份「{self.selfyear}」無效，請輸入民國年"
            return
        # 檢查月份是否為數字
        if self.selfmonth:
            try:
                int(self.selfmonth)
            except Exception as e:
                self.message = f"月份「{self.selfmonth}」無效，請輸入1～12"
                return
        self.select_value = f"{self.selfyear.zfill(3)}{self.selfmonth.zfill(2)}" if self.selfmonth else f"{self.selfyear.zfill(3)}"

    def parser(self):
        self.driver = get_driver()
        self.driver.get(self.url)
        # 進入勞動力統計頁面
        self.driver.find_element(By.LINK_TEXT, self.text_title).click()
        # 選擇城市
        if self.city:
            select_city = self.driver.find_element(By.ID, self.id_city)
            options = Select(select_city)
            options.deselect_all()
            option_city = None
            for option in options.options:
                if self.city in option.text:
                    option_city = option
                    break
            if option_city:
                driver_select(self.driver, self.id_city, "value", option_city.get_property("value"))
            else:
                self.message = f"找不到城市「{self.city}」"
                return
        btn_search = self.driver.find_element(By.ID, self.id_search)
        btn_search.click()

    def get_table(self):
        if self.selfmonth:
            check_select = self.driver.find_element(By.ID, self.id_check_year)
            select_start = self.id_start_month
            select_end = self.id_end_month
            value = f"{self.selfyear.zfill(3)}{self.selfmonth.zfill(2)}"
        else:
            check_select = self.driver.find_element(By.ID, self.id_check_month)
            select_start = self.id_start_year
            select_end = self.id_end_year
            value = self.selfyear.zfill(3)

        check_select.click()
        try:
            driver_select(self.driver, select_start, "value", value)
            driver_select(self.driver, select_end, "value", value)
        except Exception as e:
            options = self.driver.find_element(By.ID, select_start).text.replace(" ", "").replace("月", "")
            if self.selfmonth:
                options = options.replace("年", "/")
            else:
                options = options.replace("年", "")
            options = options.split("\n")
            date_start = options[0]
            date_end = options[-1]
            self.message = f"日期「{self.query_date}」無效，日期需介於「{date_start}」～「{date_end}」之間"
            return
        btn_query = self.driver.find_element(By.ID, self.id_query)
        btn_query.click()


class Insurance(WelfareApiView):
    '''
    農保api介面
    '''
    def __init__(self, command, query_date, city=None):
        self.driver = None
        self.url = "https://agrstat.coa.gov.tw/sdweb/public/inquiry/InquireAdvance.aspx"
        self.text_title = "社會保險統計"
        self.id_city = "ctl00_cphMain_uctlInquireAdvance_dtlDimension_ctl00_lstDimension"
        self.id_search = "ctl00_cphMain_uctlInquireAdvance_btnQuery"
        self.id_check_year = "ctl00_cphMain_uctlInquireAdvance_chkYear"
        self.id_start_year = "ctl00_cphMain_uctlInquireAdvance_ddlYearBegin"
        self.id_end_year = "ctl00_cphMain_uctlInquireAdvance_ddlYearEnd"
        self.id_check_month = "ctl00_cphMain_uctlInquireAdvance_chkMonth"
        self.id_start_month = "ctl00_cphMain_uctlInquireAdvance_ddlMonthBegin"
        self.id_end_month = "ctl00_cphMain_uctlInquireAdvance_ddlMonthEnd"
        self.id_query = "ctl00_cphMain_uctlInquireAdvance_btnQuery2"
        self.id_table = "ctl00_cphMain_uctlInquireAdvance_tabResult"
        self.command = command
        self.query_date = query_date
        self.city = city
        self.selfyear = ""
        self.selfmonth = None
        self.select_value = ""
        self.message = ""

        query_date = str(query_date).split("/")
        self.selfyear = query_date[0]
        if len(query_date) > 1:
            self.selfmonth = query_date[1]

    def get_result(self):
        WebDriverWait(self.driver, 30, 0.1).until(EC.presence_of_element_located((By.ID, self.id_table)))
        table = self.driver.find_element(By.ID, self.id_table)
        self.unit = "（人）"
        self.result = self.driver.find_element(By.CSS_SELECTOR, ".VerDim").parent.find_element(By.CSS_SELECTOR, ".ValueLeftTop").text

    def get_data(self):
        self.parser()
        if not self.message:
            self.get_table()
            self.get_result()
        if not self.message:
            self.message = f"搜尋「農保 {self.query_date}」的結果為：\n" + f"{self.selfyear}年"
            if self.selfmonth:
                self.message += f"{self.selfmonth}月"
            if self.city:
                self.message += f"{self.city}"
            self.message += f" 農保：{self.result}{self.unit}\n"


class Allowance(WelfareApiView):
    '''
    老農津貼api介面
    '''
    def __init__(self, command, query_date, city=None):
        self.driver = None
        self.url = "https://agrstat.coa.gov.tw/sdweb/public/inquiry/InquireAdvance.aspx"
        self.text_title = "社會福利統計"
        self.text_group = "農民健康保險投保人數"
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
        self.command = command
        self.query_date = query_date
        self.city = city
        self.selfyear = ""
        self.selfmonth = None
        self.select_value = ""
        self.message = ""

class Scholarship(WelfareApiView):
    '''
    農漁民子女獎助學金api介面
    '''
    def __init__(self, command, query_date, city=None):
        self.driver = None
        self.url = "https://agrstat.coa.gov.tw/sdweb/public/inquiry/InquireAdvance.aspx"
        self.text_title = "社會福利統計"
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
        self.command = command
        self.query_date = query_date
        self.city = city
        self.selfyear = ""
        self.selfmonth = None
        self.select_value = ""
        self.message = ""
