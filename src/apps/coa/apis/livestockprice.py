from .configs import *


class LivestockPriceApiView(ApiView):
    '''
    其他畜禽價格api介面
    -sale(拍賣價)
    -origin(產地價)
    -retail(零售價)
    畜產品價格查詢系統 http://price.naif.org.tw/Query/Query_now.aspx
    '''
    def __init__(self, command, query_date, product):
        self.driver = None
        self.url = "http://price.naif.org.tw/Query/Query_now.aspx"
        self.radio_year = "ContentPlaceHolder_content_uc_timeSelector_RadionButton_year"
        self.select_year_start_year = "ContentPlaceHolder_content_uc_timeSelector_DropDownList_startYear"
        self.select_year_end_year = "ContentPlaceHolder_content_uc_timeSelector_DropDownList_endYear"
        self.radio_month = "ContentPlaceHolder_content_uc_timeSelector_RadioButton_month"
        self.select_month_start_year = "ContentPlaceHolder_content_uc_timeSelector_DropDownList_month_startYear"
        self.select_month_end_year = "ContentPlaceHolder_content_uc_timeSelector_DropDownList_month_endYear"
        self.select_month_start_month = "ContentPlaceHolder_content_uc_timeSelector_DropDownList_month_startMonth"
        self.select_month_end_month = "ContentPlaceHolder_content_uc_timeSelector_DropDownList_month_endMonth"
        self.list_product = "ContentPlaceHolder_content_uc_productList_mixVer_Panel_data"
        self.btn_query = "ContentPlaceHolder_content_Button_query"
        self.table = "ContentPlaceHolder_content_GridView_data"
        self.xpath = "/html/body/form/div[3]/div[2]/div[2]/div/table/tbody/tr[4]/td[2]"
        self.command = command
        self.query_date = query_date
        self.product = product
        self.message = ""

    def chose_api(self):
        if self.command == "拍賣價":
            return Sale(self.command, self.query_date, self.product)
        elif self.command == "產地價":
            return Origin(self.command, self.query_date, self.product)
        elif self.command == "零售價":
            return Retail(self.command, self.query_date, self.product)

    def api(self):
        try:
            self.verify_date()
            if not self.message:
                self.get_data()
        except Exception as e:
            if not self.message:
                self.message = f"搜尋「{self.command} {self.query_date} {self.product}」發生錯誤"
        if self.driver:
            self.driver.close()
        return self.message

    def verify_date(self):
        # check years
        try:
            if '/' in self.query_date:
                self.year, self.month = self.query_date.split('/')
            else:
                self.year = self.query_date
                self.month = None
        except Exception as e:
            self.message = f"日期「{self.query_date}」發生錯誤，請輸入民國年、民國年/月份\n例如：\n108\n109/12"
            return
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
                if not 1 <= self.month <= 12:
                    self.message = f"月份「{self.month}」無效，請輸入1～12"
            except Exception as e:
                self.message = f"月份「{self.month}」無效，請輸入1～12"
                return
            self.query_date += f"{self.month}月"

    def parser(self):
        self.driver = get_driver()
        self.driver.get(self.url)

    def set_date(self):
        if self.month:
            radio_month = self.driver.find_element(By.ID, self.radio_month)
            radio_month.click()
            select_year = self.driver.find_element(By.ID, self.select_month_start_year)
            if not str(self.year) in select_year.text:
                range_year = select_year.text.replace(' ', '').split('\n')
                self.message = f"年份「{self.year - 1911}」必需在「{int(range_year[0]) - 1911}」到「{int(range_year[-1]) - 1911}」之間"
                return
            driver_select(self.driver, self.select_month_start_year, "value", str(self.year))
            driver_select(self.driver, self.select_month_start_month, "value", str(self.month))
            driver_select(self.driver, self.select_month_end_year, "value", str(self.year))
            driver_select(self.driver, self.select_month_end_month, "value", str(self.month))
        else:
            radio_year = self.driver.find_element(By.ID, self.radio_year)
            radio_year.click()
            select_year = self.driver.find_element(By.ID, self.select_year_start_year)
            if not str(self.year) in select_year.text:
                range_year = select_year.text.replace(' ', '').split('\n')
                self.message = f"年份「{self.year - 1911}」必需在「{int(range_year[0]) - 1911}」到「{int(range_year[-1]) - 1911}」之間"
                return
            driver_select(self.driver, self.select_year_start_year, "value", str(self.year))
            driver_select(self.driver, self.select_year_end_year, "value", str(self.year))

    def get_table(self):
        check_type = self.driver.find_element(By.ID, self.check_type)
        check_type.click()
        list_product = self.driver.find_element(By.ID, self.list_product)
        products = list_product.text.replace('家畜類\n', '').replace('家禽類\n', '').replace('飼料\n', '').replace(' ', '\n').split('\n')
        target_product = list()
        for product in products:
            if self.product in product:
                target_product.append(product)

        if len(target_product) == 0:
            self.list_result = None
            self.products = products
        else:
            list_result = list()
            for target in target_product:
                check_product = list_product.find_element(By.XPATH, f"//*[contains(text(), '{target}')]")
                check_product.click()
                btn_query = self.driver.find_element(By.ID, self.btn_query)
                btn_query.click()
                table = self.driver.find_element(By.ID, self.table)
                if "查無資料" in table.text:
                    list_result.append(f"{target} 查無資料")
                else:
                    data = self.driver.find_element(By.XPATH, self.xpath)
                    list_result.append(f"{target}：{data.text}(元/公斤)")
                list_product = self.driver.find_element(By.ID, self.list_product)
                check_product = list_product.find_element(By.XPATH, f"//*[contains(text(), '{target}')]")
                check_product.click()
                list_product = self.driver.find_element(By.ID, self.list_product)
            self.list_result = list_result

    def get_data(self):
        self.parser()
        self.set_date()
        if self.message:
            return
        self.get_table()
        if self.list_result:
            self.message = f"{self.query_date} {self.product} {self.command}：\n"
            for result in self.list_result:
                self.message += f"{result}\n"
            if self.message.endswith('\n'):
                self.message = self.message[:-1]
        else:
            self.message = f"找不到品項「{self.product}」，可使用的品項如下：\n" + "、".join(product for product in self.products)


class Sale(LivestockPriceApiView):
    '''
    拍賣價api介面
    '''
    def __init__(self, *args):
        super(Sale, self).__init__(*args)
        self.check_type = "ContentPlaceHolder_content_uc_productList_mixVer_CheckBoxList_priceType_1"


class Origin(LivestockPriceApiView):
    '''
    產地價api介面
    '''
    def __init__(self, *args):
        super(Origin, self).__init__(*args)
        self.check_type = "ContentPlaceHolder_content_uc_productList_mixVer_CheckBoxList_priceType_0"


class Retail(LivestockPriceApiView):
    '''
    零售價api介面
    '''
    def __init__(self, *args):
        super(Retail, self).__init__(*args)
        self.check_type = "ContentPlaceHolder_content_uc_productList_mixVer_CheckBoxList_priceType_2"
