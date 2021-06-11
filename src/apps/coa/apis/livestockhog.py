from .configs import *


class LivestockHogApiView(ApiView):
    '''
    毛豬價格api介面
    -amount(交易量)
    -sale(拍賣價)
    -weight(平均重量)
    畜產行情資訊網 http://ppg.naif.org.tw/naif/MarketInformation/Pig/twStatistics.aspx
    '''
    def __init__(self, command, query_date):
        self.driver = None
        self.url = "http://ppg.naif.org.tw/naif/MarketInformation/Pig/twStatistics.aspx"
        self.check_month = "ContentPlaceHolder_contant_ContentPlaceHolder_contant_RadioButton_m"
        self.select_month_start_year = "ContentPlaceHolder_contant_ContentPlaceHolder_contant_DropDownList_m_begYear"
        self.select_month_start_month = "ContentPlaceHolder_contant_ContentPlaceHolder_contant_DropDownList_m_begMonth"
        self.select_month_end_year = "ContentPlaceHolder_contant_ContentPlaceHolder_contant_DropDownList_m_endYear"
        self.select_month_end_month = "ContentPlaceHolder_contant_ContentPlaceHolder_contant_DropDownList_m_endMonth"
        self.check_year = "ContentPlaceHolder_contant_ContentPlaceHolder_contant_RadioButton_y"
        self.select_year_start_year = "ContentPlaceHolder_contant_ContentPlaceHolder_contant_DropDownList_y_beg"
        self.select_year_end_year = "ContentPlaceHolder_contant_ContentPlaceHolder_contant_DropDownList_y_end"
        self.check_penghu = "ContentPlaceHolder_contant_ContentPlaceHolder_contant_CheckBox_penghu"
        self.btn_query = "ContentPlaceHolder_contant_ContentPlaceHolder_contant_Button_query"
        self.table = "ContentPlaceHolder_contant_ContentPlaceHolder_contant_GridView_data"
        self.xpath_amount = "/html/body/form/div[3]/div[2]/div[2]/div[1]/table/tbody/tr[3]/td[5]"
        self.xpath_sale = "/html/body/form/div[3]/div[2]/div[2]/div[1]/table/tbody/tr[3]/td[7]"
        self.xpath_weight = "/html/body/form/div[3]/div[2]/div[2]/div[1]/table/tbody/tr[3]/td[6]"
        self.command = command
        self.query_date = query_date
        self.message = ""

    def api(self):
        try:
            self.verify_date()
            if not self.message:
                self.get_data()
        except Exception as e:
            if not self.message:
                self.message = f"搜尋「{self.command} {self.query_date}」發生錯誤"
        if self.driver:
            self.driver.close()
        return self.message

    def verify_date(self):
        # check years
        if '/' in self.query_date:
            self.year, self.month = self.query_date.split('/')
        else:
            self.year = self.query_date
            self.month = None
        # 檢查年份是否為數字
        try:
            self.year = int(self.year)
            self.year += 1911
        except Exception as e:
            self.message = f"年份「{self.year}」無效，請輸入民國年"
            return
        self.query_date = f"{self.year - 1911}年"
        # 檢查月份是否為數字
        if self.month:
            try:
                self.month = int(self.month)
            except Exception as e:
                self.message = f"月份「{self.month}」無效，請輸入1～12"
                return
            self.query_date += f"{self.month}月"

    def parser(self):
        self.driver = get_driver(False)
        self.driver.get(self.url)

    def get_table(self):
        if self.month:
            btn_check_month = self.driver.find_element(By.ID, self.check_month)
            btn_check_month.click()
            driver_select(self.driver, self.select_month_start_year, "value", str(self.year))
            driver_select(self.driver, self.select_month_start_month, "value", str(self.month))
            driver_select(self.driver, self.select_month_end_year, "value", str(self.year))
            driver_select(self.driver, self.select_month_end_month, "value", str(self.month))
        else:
            btn_check_year = self.driver.find_element(By.ID, self.check_year)
            btn_check_year.click()
            driver_select(self.driver, self.select_year_start_year, "value", str(self.year))
            driver_select(self.driver, self.select_year_end_year, "value", str(self.year))
        btn_check_penghu = self.driver.find_element(By.ID, self.check_penghu)
        btn_check_penghu.click()
        btn_query = self.driver.find_element(By.ID, self.btn_query)
        btn_query.click()

    def get_data(self):
        self.parser()
        self.get_table()
        amount = self.driver.find_element(By.XPATH, self.xpath_amount).text
        sale = self.driver.find_element(By.XPATH, self.xpath_sale).text
        weight = self.driver.find_element(By.XPATH, self.xpath_weight).text
        self.message = f"{self.query_date} 豬\n成交頭數：{amount}(頭)\n平均重量：{weight}(公斤)\n平均價格(規格豬)：{sale}(元/公斤)"
