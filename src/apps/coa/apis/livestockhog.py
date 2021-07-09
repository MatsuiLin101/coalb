from .configs import *


class LivestockHogApiView(BasicApiView):
    '''
    毛豬價格api介面
    -amount(交易量)
    -price(價格)
    -weight(重量)
    畜產行情資訊網 http://ppg.naif.org.tw/naif/MarketInformation/Pig/twStatistics.aspx
    '''
    def __init__(self, params):
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
        self.xpath_price = "/html/body/form/div[3]/div[2]/div[2]/div[1]/table/tbody/tr[3]/td[7]"
        self.xpath_weight = "/html/body/form/div[3]/div[2]/div[2]/div[1]/table/tbody/tr[3]/td[6]"
        self.message = ""
        self.params = params

        if not 2 <= len(params) <= 3:
            raise CustomError(f"毛豬(不包含澎湖)的指令為「毛豬 年份」或「毛豬 年份/月份」，例如：\n「毛豬 108」\n「毛豬 108/12」\n\n也使用替代指令查詢(皆可帶入月份)，例如：\n「交易量 豬 107」\n「價格 豬 108/12」\n「重量 豬 109/1」")
        self.command = params[0]
        if len(params) == 2:
            self.query_date = params[1]
        else:
            self.product = params[1]
            self.query_date = params[2]
        self.command_text = " ".join(text for text in params)

    def verify_date(self):
        try:
            if '/' in self.query_date:
                self.year, self.month = self.query_date.split('/')
            else:
                self.year = self.query_date
                self.month = None
        except Exception as e:
            self.message = f"日期「{self.query_date}」發生錯誤，請輸入民國年、民國年/月份\n例如：\n108\n109/12"
            raise CustomError(self.message)
        # 檢查年份是否為數字
        try:
            self.year = int(self.year)
            self.year += 1911
        except Exception as e:
            self.message = f"年份「{self.year}」無效，請輸入民國年"
            raise CustomError(self.message)
        # 檢查月份是否為數字
        if self.month:
            try:
                self.month = int(self.month)
                if not 1 <= self.month <= 12:
                    self.message = f"月份「{self.month}」無效，請輸入1～12"
                    raise CustomError(self.message)
            except Exception as e:
                self.message = f"月份「{self.month}」無效，請輸入1～12"
                raise CustomError(self.message)

    def get_table(self):
        if self.month:
            btn_check_month = self.driver.find_element(By.ID, self.check_month)
            btn_check_month.click()
            select_year = self.driver.find_element(By.ID, self.select_month_start_year)
            if not str(self.year) in select_year.text:
                range_year = select_year.text.replace(' ', '').split('\n')
                self.message = f"年份「{self.year - 1911}」必需在「{int(range_year[0]) - 1911}」到「{int(range_year[-1]) - 1911}」之間"
                raise CustomError(self.message)
            driver_select(self.driver, self.select_month_start_year, "value", str(self.year))
            driver_select(self.driver, self.select_month_start_month, "value", str(self.month))
            driver_select(self.driver, self.select_month_end_year, "value", str(self.year))
            driver_select(self.driver, self.select_month_end_month, "value", str(self.month))
        else:
            btn_check_year = self.driver.find_element(By.ID, self.check_year)
            btn_check_year.click()
            select_year = self.driver.find_element(By.ID, self.select_year_start_year)
            if not str(self.year) in select_year.text:
                range_year = select_year.text.replace(' ', '').split('\n')
                self.message = f"年份「{self.year - 1911}」必需在「{int(range_year[0]) - 1911}」到「{int(range_year[-1]) - 1911}」之間"
                raise CustomError(self.message)
            driver_select(self.driver, self.select_year_start_year, "value", str(self.year))
            driver_select(self.driver, self.select_year_end_year, "value", str(self.year))
        btn_check_penghu = self.driver.find_element(By.ID, self.check_penghu)
        btn_check_penghu.click()
        btn_query = self.driver.find_element(By.ID, self.btn_query)
        btn_query.click()

    def get_data(self):
        self.parser()
        self.get_table()
        table = self.driver.find_element(By.ID, self.table)
        if "查無資料" in table.text:
            if self.month:
                self.message = f"{self.year - 1911}年{self.month}月 豬 查無資料"
            else:
                self.message = f"{self.year - 1911}年 豬 查無資料"
            return
        amount = self.driver.find_element(By.XPATH, self.xpath_amount).text
        price = self.driver.find_element(By.XPATH, self.xpath_price).text
        weight = self.driver.find_element(By.XPATH, self.xpath_weight).text
        if self.month:
            self.message = f"{self.year - 1911}年{self.month}月 豬(不含澎湖)\n成交頭數：{amount}(頭)\n平均重量：{weight}(公斤)\n平均價格(規格豬)：{price}(元/公斤)"
        else:
            self.message = f"{self.year - 1911}年 豬(不含澎湖)\n成交頭數：{amount}(頭)\n平均重量：{weight}(公斤)\n平均價格(規格豬)：{price}(元/公斤)"
