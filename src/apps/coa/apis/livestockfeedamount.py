from .configs import *


class LivestockFeedamountApiView(ApiView):
    '''
    畜禽在養數量api介面
    -feedamount(在養數量)
    動態查詢 [農業生產統計]>>[畜禽產品飼養數量統計]>>[家畜飼養頭數]、[家禽飼養隻數：縣市別×家禽別(104年度起)]
    https://agrstat.coa.gov.tw/sdweb/public/inquiry/InquireAdvance.aspx
    '''
    def __init__(self, query_date, product, city=None):
        super()
        self.driver = None
        self.url = "https://agrstat.coa.gov.tw/sdweb/public/inquiry/InquireAdvance.aspx"
        self.text_title = "畜禽產品飼養數量統計"
        self.text_group1 = "家畜飼養頭數"
        self.text_group2 = "家禽飼養隻數：縣市別×家禽別(104年度起)"
        self.id_group = "ctl00_cphMain_uctlInquireAdvance_lstFieldGroup"
        self.id_city = "ctl00_cphMain_uctlInquireAdvance_dtlDimension_ctl00_lstDimension"
        self.id_product = "ctl00_cphMain_uctlInquireAdvance_dtlDimension_ctl02_lstDimension"
        self.id_search = "ctl00_cphMain_uctlInquireAdvance_btnQuery"
        self.id_check_year = "ctl00_cphMain_uctlInquireAdvance_chkYear"
        self.id_start_year = "ctl00_cphMain_uctlInquireAdvance_ddlYearBegin"
        self.id_end_year = "ctl00_cphMain_uctlInquireAdvance_ddlYearEnd"
        self.id_query = "ctl00_cphMain_uctlInquireAdvance_btnQuery2"
        self.id_table = "ctl00_cphMain_uctlInquireAdvance_tabResult"
        self.query_date = str(query_date)
        self.product = product
        self.city =  city
        self.group = None
        self.message = ""

        if self.city is not None:
            self.city = city.replace('台', '臺')

    def api(self):
        try:
            self.check_year()
            if not self.message:
                self.get_data()
        except Exception as e:
            print(traceback.format_exc())
            if not self.message:
                self.message = f"搜尋「在養量 {self.query_date} {self.product}」發生錯誤"
        if self.driver:
            self.driver.close()
        return self.message

    def check_year(self):
        # check years
        # 檢查年份是否為數字
        try:
            self.year = int(self.query_date)
        except Exception as e:
            self.message = f"年份「{self.query_date}」無效，請輸入民國年"
            return

    def parser(self):
        self.driver = get_driver()
        self.driver.get(self.url)
        # 進入畜禽產品飼養數量統計頁面
        self.driver.find_element(By.LINK_TEXT, self.text_title).click()

    def get_group(self):
        # 根據使用者輸入的product選擇對應的group
        # 是否有完全符合name的物件
        try:
            self.obj_product = LivestockFeedamount.objects.get(name=self.product, sub_class="product")
            return
        except Exception as e:
            pass

        # 是否有部分符合name的物件
        try:
            self.obj_product = LivestockFeedamount.objects.get(name__icontains=self.product, sub_class="product")
            return
        except Exception as e:
            pass

        # 是否有完全符合search_name的物件
        try:
            self.obj_product = LivestockFeedamount.objects.get(search_name=self.product, sub_class="product")
            return
        except Exception as e:
            pass

        # 可能有多種結果，請使用者改用詳細關鍵字
        qs = LivestockFeedamount.objects.filter(name__icontains=self.product, sub_class="product")
        if qs.count() > 0:
            list_product = list(qs.values_list("name", flat=True))
            message = '\n'.join([product for product in list_product])
            self.message = f"品項「{self.product}」有多個搜尋結果，請改用完整關鍵字如下：\n" + message
        else:
            self.message = f"查無品項「{self.product}」"

    def get_city(self):
        # 是否有完全符合name的物件
        try:
            self.obj_city = LivestockFeedamount.objects.get(name=self.city, main_class=self.obj_product.main_class, sub_class="city")
            return
        except Exception as e:
            pass

        # 是否有部分符合name的物件
        try:
            self.obj_city = LivestockFeedamount.objects.get(name__icontains=self.city, main_class=self.obj_product.main_class, sub_class="city")
            return
        except Exception as e:
            pass

        # 是否有完全符合search_name的物件
        try:
            self.obj_city = LivestockFeedamount.objects.get(search_name=self.city, main_class=self.obj_product.main_class, sub_class="city")
            return
        except Exception as e:
            pass

        # 可能有多種結果，請使用者改用詳細關鍵字
        qs = LivestockFeedamount.objects.filter(name__icontains=self.city, main_class=self.obj_product.main_class, sub_class="city")
        if qs.count() > 0:
            list_city = list(qs.values_list("search_name", flat=True))
            message = '\n'.join([city for city in list_city])
            self.message = f"城市「{self.city}」有多個搜尋結果，請改用完整關鍵字如下：\n" + message
        else:
            self.message = f"查無城市「{self.city}」"

    def get_query(self):
        # 選擇主分類
        if self.obj_product.main_class == self.text_group1:
            group = self.text_group1
        else:
            group = self.text_group2
        driver_select(self.driver, self.id_group, "text", group)
        # 選擇城市
        if self.city is not None:
            time.sleep(1)
            driver_select(self.driver, self.id_city, "value", self.obj_city.value, True)
        # 選擇產品
        time.sleep(1)
        driver_select(self.driver, self.id_product, "value", self.obj_product.value, True)
        # 送出查詢
        btn_search = self.driver.find_element(By.ID, self.id_search)
        btn_search.click()

    def get_table(self):
        # select_start_year = self.driver.find_element(By.ID, self.id_start_year)
        # select_end_year = self.driver.find_element(By.ID, self.id_end_year)
        value = str(self.year).zfill(3)
        try:
            driver_select(self.driver, self.id_start_year, "value", value)
            driver_select(self.driver, self.id_end_year, "value", value)
        except Exception as e:
            options = self.driver.find_element(By.ID, self.id_start_year).text.replace(" ", "").replace("年", "")
            options = options.split("\n")
            date_start = options[0]
            date_end = options[-1]
            self.message = f"年份「{self.query_date}」超出範圍，年份需介於「{date_start}」～「{date_end}」之間"
            return

        btn_query = self.driver.find_element(By.ID, self.id_query)
        btn_query.click()

    def get_result(self):
        WebDriverWait(self.driver, 30, 0.1).until(EC.presence_of_element_located((By.ID, self.id_table)))
        table = self.driver.find_element(By.ID, self.id_table)
        self.result = self.driver.find_element(By.CSS_SELECTOR, ".VerDim").parent.find_element(By.CSS_SELECTOR, ".ValueLeftTop").text

    def get_data(self):
        self.parser()
        self.get_group()
        if self.message:
            return
        if self.city is not None:
            self.get_city()
        if self.message:
            return
        self.get_query()
        self.get_table()
        if self.message:
            return
        self.get_result()
        if not self.message:
            self.message = f"搜尋「在養量 {self.year} {self.product}_city_1」的結果為：\n" + f"{self.year}年 {self.obj_product.name}_city_2 在養量：{self.result}(頭)"
            if self.city is not None:
                self.message = self.message.replace('_city_1', f' {self.city}')
                self.message = self.message.replace('_city_2', f' {self.obj_city}')
            else:
                self.message = self.message.replace('_city_1', '')
                self.message = self.message.replace('_city_2', '')
