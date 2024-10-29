from .configs import *


class WelfareApiView(BasicApiView):
    '''
    社會福利api介面
    welfare(社會福利)
    -Insurance(農保)
    動態查詢 [社會保險及社會指標統計]>>[社會保險統計]>>[農民健康保險投保人數]
    https://agrstat.moa.gov.tw/sdweb/public/inquiry/InquireAdvance.aspx
    -Allowance(老農津貼)
    動態查詢 [社會保險及社會指標統計]>>[社會福利統計]>>[老農津貼人數]、[老農津貼金額]
    https://agrstat.moa.gov.tw/sdweb/public/inquiry/InquireAdvance.aspx
    -Scholarship(農漁民子女獎助學金)
    動態查詢 [社會保險及社會指標統計]>>[社會福利統計]>>[農漁民子弟就學獎助學金發放件數]、[農漁民子弟就學獎助學金發放金額：縣市別]
    https://agrstat.moa.gov.tw/sdweb/public/inquiry/InquireAdvance.aspx
    '''
    def __init__(self, params):
        self.driver = None
        self.url = "https://agrstat.moa.gov.tw/sdweb/public/inquiry/InquireAdvance.aspx"
        self.id_group = "ctl00_cphMain_uctlInquireAdvance_lstFieldGroup"
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
        self.id_back = "ctl00_cphMain_uctlInquireAdvance_btnBack2"
        self.year = ""
        self.month = ""
        self.option_city = None
        self.message = ""
        self.params = params
        self.command = params[0]

    def choose_api(self):
        if self.command in ["農保"]:
            return Insurance(self.params)
        elif self.command in ["津貼", "老農津貼"]:
            return Allowance(self.params)
        elif self.command in ["獎助學金"]:
            return Scholarship(self.params)

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

    def parser(self, group=None, text=None):
        super(WelfareApiView, self).parser()
        # 進入勞動力統計頁面
        self.driver.find_element(By.LINK_TEXT, self.text_title).click()
        # 選擇分類
        if group:
            driver_select(self.driver, group, "text", text)
            time.sleep(1)
        # 選擇城市
        if self.city:
            select_city = self.driver.find_element(By.ID, self.id_city)
            options = Select(select_city)
            for option in options.options:
                if self.city in option.text:
                    self.option_city = option
                    break
            if self.option_city:
                driver_select(self.driver, self.id_city, "value", self.option_city.get_property("value"), True)
            else:
                self.message = f"找不到城市「{self.city}」"
                raise CustomError(self.message)
        btn_search = self.driver.find_element(By.ID, self.id_search)
        btn_search.click()

    def parser_second(self, group=None, text=None):
        btn_back = self.driver.find_element(By.ID, self.id_back)
        btn_back.click()
        # 選擇分類
        driver_select(self.driver, group, "text", text)
        time.sleep(1)
        # 選擇城市
        if self.city:
            select_city = self.driver.find_element(By.ID, self.id_city)
            options = Select(select_city)
            for option in options.options:
                if self.city in option.text:
                    self.option_city = option
                    break
            if self.option_city:
                driver_select(self.driver, self.id_city, "value", self.option_city.get_property("value"), True)
            else:
                self.message = f"找不到城市「{self.city}」"
                return
        btn_search = self.driver.find_element(By.ID, self.id_search)
        btn_search.click()

    def get_table(self):
        '''
        可能只有年資料或只有月資料
        '''
        try:
            self.driver.find_element(By.ID, self.id_check_month)
        except Exception as e:
            if self.month:
                select_start = self.id_start_year
                options = self.driver.find_element(By.ID, select_start).text.replace(" ", "").replace("月", "").replace("年", "")
                options = options.split("\n")
                date_start = options[0]
                date_end = options[-1]
                if self.city:
                    self.message = f"「{self.command} {self.city}」沒有月份的資料，請選擇年份「{date_start}」～「{date_end}」"
                else:
                    self.message = f"「{self.command}」沒有月份的資料，請選擇年份「{date_start}」～「{date_end}」"
                raise CustomError(self.message)
        try:
            self.driver.find_element(By.ID, self.id_check_year)
        except Exception as e:
            if not self.month:
                select_start = self.id_start_month
                options = self.driver.find_element(By.ID, select_start).text.replace(" ", "").replace("月", "").replace("年", "/")
                options = options.split("\n")
                date_start = options[0]
                date_end = options[-1]
                if self.city:
                    self.message = f"「{self.command} {self.city}」沒有年份的資料，請選擇日期「{date_start}」～「{date_end}」"
                else:
                    self.message = f"「{self.command}」沒有年份的資料，請選擇日期「{date_start}」～「{date_end}」"
                raise CustomError(self.message)
        if self.month:
            try:
                check_select = self.driver.find_element(By.ID, self.id_check_year)
                check_select.click()
            except Exception as e:
                pass
            select_start = self.id_start_month
            select_end = self.id_end_month
        else:
            try:
                check_select = self.driver.find_element(By.ID, self.id_check_month)
                check_select.click()
            except Exception as e:
                pass
            select_start = self.id_start_year
            select_end = self.id_end_year

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
        self.result = self.driver.find_element(By.CSS_SELECTOR, ".VerDim").parent.find_element(By.CSS_SELECTOR, ".ValueLeftTop").text


class Insurance(WelfareApiView):
    '''
    農保api介面
    '''
    def __init__(self, params):
        super(Insurance, self).__init__(params)
        self.text_title = "社會保險統計"

        if not 2 <= len(params) <= 3:
            raise CustomError(f"農保的指令為「農保 年份」或「農保 年份/月份」，例如：\n「農保 108」\n「農保 108/3」\n\n也可加上縣市「農保 縣市 年份」或「農保 縣市 年份/月份」，例如：\n「農保 高雄 109」\n「農保 高雄 109/3」")
        self.command = params[0]
        if len(params) == 3:
            self.city = params[1].replace("台", "臺")
            self.query_date = params[2]
        else:
            self.city = None
            self.query_date = params[1]
        self.command_text = " ".join(text for text in params)

    def get_data(self):
        self.parser()
        self.get_table()
        self.get_result()

        self.message = f"{self.year}年_month__city_ 農保：{self.result}(人)"
        if self.month:
            self.message = self.message.replace('_month_', f'{self.month}月')
        else:
            self.message = self.message.replace('_month_', '')
        if self.city:
            self.message = self.message.replace('_city_', f' {self.city}')
        else:
            self.message = self.message.replace('_city_', '')


class Allowance(WelfareApiView):
    '''
    老農津貼api介面
    '''
    def __init__(self, params):
        super(Allowance, self).__init__(params)
        self.text_title = "社會福利統計"
        self.text_group_1 = "老農津貼人數"
        self.text_group_2 = "老農津貼金額"

        if not 2 <= len(params) <= 3:
            raise CustomError(f"老農津貼的指令為「老農津貼 年份」或「老農津貼 年份/月份」，例如：\n「老農津貼 108」\n「老農津貼 108/3」\n\n也可加上縣市「老農津貼 縣市 年份」或「老農津貼 縣市 年份/月份」，例如：\n「老農津貼 高雄 109」\n「老農津貼 高雄 109/3」")
        self.command = params[0]
        if len(params) == 3:
            self.city = params[1].replace("台", "臺")
            self.query_date = params[2]
        else:
            self.city = None
            self.query_date = params[1]
        self.command_text = " ".join(text for text in params)

    def get_data(self):
        self.parser(self.id_group, self.text_group_1)
        self.get_table()
        self.get_result()
        result1 = self.result
        self.parser_second(self.id_group, self.text_group_2)
        self.get_table()
        self.get_result()
        result2 = self.result

        self.message = f"{self.year}年_month__city_ 老農津貼人數：{result1}(人)\n"
        self.message += f"{self.year}年_month__city_ 老農津貼金額：{result2}(元)"
        if self.month:
            self.message = self.message.replace('_month_', f'{self.month}月')
        else:
            self.message = self.message.replace('_month_', '')
        if self.city:
            self.message = self.message.replace('_city_', f' {self.city}')
        else:
            self.message = self.message.replace('_city_', '')


class Scholarship(WelfareApiView):
    '''
    農漁民子女獎助學金api介面
    '''
    def __init__(self, params):
        super(Scholarship, self).__init__(params)
        self.text_title = "社會福利統計"
        self.text_group_1 = "農漁民子弟就學獎助學金發放件數"
        self.text_group_2 = "農漁民子弟就學獎助學金發放金額：縣市別"

        if not 2 <= len(params) <= 3:
            raise CustomError(f"獎助學金的指令為「獎助學金 年份」或「獎助學金 年份/月份」，例如：\n「獎助學金 108」\n「獎助學金 108/3」\n\n也可加上縣市「獎助學金 縣市 年份」或「獎助學金 縣市 年份/月份」，例如：\n「獎助學金 高雄 109」\n「獎助學金 高雄 109/3」")
        self.command = params[0]
        if len(params) == 3:
            self.city = params[1].replace("台", "臺")
            self.query_date = params[2]
        else:
            self.city = None
            self.query_date = params[1]
        self.command_text = " ".join(text for text in params)

    def get_data(self):
        self.parser(self.id_group, self.text_group_1)
        self.get_table()
        self.get_result()
        result1 = self.result
        self.parser_second(self.id_group, self.text_group_2)
        self.get_table()
        self.get_result()
        result2 = self.result

        self.message = f"{self.year}年_month__city_ 農漁民子女獎助學金發放件數：{result1}(件)\n"
        self.message += f"{self.year}年_month__city_ 農漁民子女獎助學金金額：{result2}(元)"
        if self.month:
            self.message = self.message.replace('_month_', f'{self.month}月')
        else:
            self.message = self.message.replace('_month_', '')
        if self.city:
            self.message = self.message.replace('_city_', f' {self.city}')
        else:
            self.message = self.message.replace('_city_', '')
