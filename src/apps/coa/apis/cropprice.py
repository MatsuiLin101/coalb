from .configs import *


class CropPriceApiView(BasicApiView):
    '''
    農耕價格api介面
    -price(價格)
    -—產地價
    農糧署農產品產地價格查報系統
    https://apis.afa.gov.tw/pagepub/AppContentPage.aspx?itemNo=PRI105
    —-批發價
    動態查詢 [農產品運銷統計]>>[農產品價格統計]>>[蔬菜批發價格：蔬菜別]、[果品批發價格：果品別]、[白米批發(躉售)價格：稻種別]
    https://agrstat.moa.gov.tw/sdweb/public/inquiry/InquireAdvance.aspx
    '''
    def __init__(self, params):
        self.params = params
        self.command = params[0]

    def choose_api(self):
        if self.command in ["產地"]:
            return CropPriceOriginApiView(self.params, use_proxy=True)
        elif self.command in ["批發"]:
            return CropPriceWholesaleApiView(self.params)

    def verify_date(self):
        # 檢查年份是否為數字
        if '/' in self.query_date:
            self.year, self.month = self.query_date.split('/')
        else:
            self.year = self.query_date
            self.month = None
        try:
            self.year = int(self.year)
            self.query_date = f"{self.year}年"
            self.select_date = str(self.year).zfill(3)
        except Exception as e:
            self.message = f"年份「{self.year}」無效，請輸入民國年"
            raise CustomError(self.message)
        if self.month:
            try:
                self.month = int(self.month)
                self.select_date += str(self.month).zfill(2)
                if not 1 <= self.month <= 12:
                    self.message = f"月份「{self.month}」請輸入1~12"
                    raise CustomError(self.message)
                self.query_date += f"{self.month}月"
            except Exception as e:
                self.message = f"月份「{self.month}」無效，請輸入1~12"
                raise CustomError(self.message)


class CropPriceOriginApiView(CropPriceApiView):
    '''
    農耕價格api介面
    -price(價格)
    -—產地價
    農糧署農產品產地價格查報系統
    https://apis.afa.gov.tw/pagepub/AppContentPage.aspx?itemNo=PRI105
    '''
    def __init__(self, params, use_proxy=False):
        self.driver = None
        self.url = "https://apis.afa.gov.tw/pagepub/AppContentPage.aspx?itemNo=PRI105"
        self.id_radio_month = "WR1_1_Q_AvgPriceType_C1_1"
        self.id_select_year_start = "WR1_1_Q_PRSR_Year1_C1"
        self.id_select_year_end = "WR1_1_Q_PRSR_Year2_C1"
        self.id_select_month_start = "WR1_1_Q_PRSR_Month1_C1"
        self.id_select_month_end = "WR1_1_Q_PRSR_Month2_C1"
        self.id_category = "WR1_1_Q_GroupCode_XX_C1"
        self.id_result_table = "WR1_1_WG1"
        self.year = ""
        self.month = ""
        self.result = list()
        self.message = ""
        self.params = params
        self.use_proxy = use_proxy

        if not 3 <= len(params) <= 4:
            raise CustomError(f"產地價的指令為「產地 品項 年份」也可加上縣市或月份「產地 縣市 品項 年份/月份」，例如：\n「產地 芒果 108」\n「產地 芒果 108/12」\n「產地 屏東 芒果 108」\n「產地 屏東 芒果 108/12」")
        self.command = params[0]
        if len(params) == 3:
            self.city = None
            self.product = params[1]
            self.query_date = params[2]
        else:
            self.city = params[1].replace("臺", "台")
            self.product = params[2]
            self.query_date = params[3]
        self.command_text = " ".join(text for text in params)

    def execute_api(self):
        if self.use_proxy:
            # data = {
            #     'params': self.params
            # }
            data = "__paramlink__".join(params for params in self.params)
            res = requests.get(f"{settings.PROXY_DOMAIN}{reverse('coa:proxy_parser')}?token={settings.PROXY_TOKEN}&api=CropPriceOriginApiView&data={data}")
            if res.status_code != 200:
                return '該功能維護中...'
            return res.text
        else:
            return super(CropPriceOriginApiView, self).execute_api()

    def get_product(self):
        qs = CropPriceOrigin.objects.filter(name__icontains=self.product)
        if qs.count() == 0:
            self.message = f"查無品項「{self.product}」"
            raise CustomError(self.message)
        elif qs.count() > 5:
            self.message = f"搜尋品項「{self.product}」結果過多，請修改關鍵字後重新查詢：\n" + "\n".join(obj.name for obj in qs)
            raise CustomError(self.message)
        else:
            self.query_set = qs

    def set_query(self):
        if self.month:
            radio_month = self.driver.find_element(By.ID, self.id_radio_month)
            radio_month.click()
            WebDriverWait(self.driver, 30, 0.1).until(EC.presence_of_element_located((By.ID, self.id_select_month_start)))
            # select_month_start = self.driver.find_element(By.ID, self.id_select_month_start)
            # select_month_end = self.driver.find_element(By.ID, self.id_select_month_end)
            driver_select(self.driver, self.id_select_month_start, "value", str(self.month))
            driver_select(self.driver, self.id_select_month_end, "value", str(self.month))

        # select_year_start = self.driver.find_element(By.ID, self.id_select_year_start)
        # select_year_end = self.driver.find_element(By.ID, self.id_select_year_end)
        try:
            driver_select(self.driver, self.id_select_year_start, "value", str(self.year + 1911))
            driver_select(self.driver, self.id_select_year_end, "value", str(self.year + 1911))
        except Exception as e:
            select_year_start = self.driver.find_element(By.ID, self.id_select_year_start)
            options_year = select_year_start.find_elements(By.TAG_NAME, 'option')
            option_year_start = int(options_year[0].text) - 1911
            option_year_end = int(options_year[-1].text) - 1911
            self.message = f"年份「{self.year}」超過範圍，請輸入{option_year_start}～{option_year_end}"
            raise CustomError(self.message)

    def get_query(self, obj):
        select_category = self.driver.find_element(By.ID, self.id_category)
        obj_category = obj.category
        obj_id_table = obj.id_table
        obj_id_query = obj.id_query
        obj_id = obj.code
        obj_name = obj.name
        driver_select(self.driver, self.id_category, "text", obj_category)
        WebDriverWait(self.driver, 30, 0.1).until(EC.presence_of_element_located((By.ID, obj_id_table)))
        btn_product = self.driver.find_element(By.ID, obj_id)
        btn_product.click()
        btn_query = self.driver.find_element(By.ID, obj_id_query)
        btn_query.find_element(By.TAG_NAME, 'a').click()

    def get_result(self):
        while len(self.driver.window_handles) == 1:
            time.sleep(0.1)
        window_origin = self.driver.window_handles[0]
        window_new = self.driver.window_handles[-1]
        self.driver.switch_to_window(window_new)
        WebDriverWait(self.driver, 30, 0.1).until(EC.presence_of_element_located((By.ID, self.id_result_table)))
        result_table = self.driver.find_element(By.ID, self.id_result_table)
        result = result_table.text
        self.driver.close()
        self.driver.switch_to_window(window_origin)
        return result

    def calc_result(self):
        self.list_result = list()
        for result in self.result:
            total = 0
            obj = result[0]
            data = result[1]
            rows = data.split('\n')[1:]
            if len(rows) == 0:
                self.list_result.append(f"{obj.name}：查無結果。")
            elif self.city:
                # 有指定縣市
                for row in rows:
                    if self.city in row:
                        cell = row.split(' ')
                        self.list_result.append((obj, f"{cell[0]} {cell[1]}：{round(float(cell[2]), 2)}(元/公斤)"))
            else:
                # 沒有指定縣市
                for row in rows:
                    total += float(row.split(' ')[-1])
                avg_total = round(total / len(rows), 2)
                self.list_result.append(f"{obj.name}：{avg_total}(元/公斤)")

    def get_data(self):
        self.parser()
        self.get_product()
        self.set_query()
        for obj in self.query_set:
            self.get_query(obj)
            result = self.get_result()
            self.result.append((obj, result))
        self.calc_result()
        if self.city:
            self.message = f"{self.year}年_month_ {self.city} {self.product} 產地價：\n"
            product = None
            for result in self.list_result:
                if type(result) == str:
                    self.message += f"{result}\n"
                    continue
                if product != result[0]:
                    product = result[0]
                    self.message += f"{product}\n"
                self.message += f"{result[1]}\n"
            self.message = self.message[:-1]
        else:
            self.message = f"{self.year}年_month_ {self.product} 產地價：\n" + "\n".join(result for result in self.list_result)
        if self.month:
            self.message = self.message.replace('_month_', f'{self.month}月')
        else:
            self.message = self.message.replace('_month_', '')


class CropPriceWholesaleApiView(CropPriceApiView):
    '''
    —-批發價
    動態查詢 [農產品運銷統計]>>[農產品價格統計]>>[蔬菜批發價格：蔬菜別]、[果品批發價格：果品別]、[白米批發(躉售)價格：稻種別]
    https://agrstat.moa.gov.tw/sdweb/public/inquiry/InquireAdvance.aspx
    '''
    def __init__(self, params):
        self.driver = None
        self.url = "https://agrstat.moa.gov.tw/sdweb/public/inquiry/InquireAdvance.aspx"
        self.text_title = "農產品價格統計"
        self.text_group1 = "蔬菜批發價格：蔬菜別"
        self.text_group2 = "果品批發價格：果品別"
        self.text_group3 = "白米批發(躉售)價格：稻種別"
        self.id_group = "ctl00_cphMain_uctlInquireAdvance_lstFieldGroup"
        self.id_product = "ctl00_cphMain_uctlInquireAdvance_dtlDimension_ctl00_lstDimension"
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
        self.option_selected = None
        self.result = list()
        self.message = ""
        self.params = params

        if len(params) != 3:
            raise CustomError(f"批發的指令為「批發 品項 年份」也可加上月份「批發 品項 年份/月份」，例如：\n「批發 甘藍 108」\n「批發 甘藍 109/1」")
        self.command = params[0]
        self.product = params[1]
        self.query_date = params[2]
        self.command_text = " ".join(text for text in params)

    def parser(self):
        super(CropPriceWholesaleApiView, self).parser()
        # 進入農產品價格統計頁面
        self.driver.find_element(By.LINK_TEXT, self.text_title).click()

    def get_product(self):
        # 根據使用者輸入的product選擇對應的group
        # 可能有多種結果，請使用者改用詳細關鍵字
        qs = CropPriceWholesale.objects.filter(name=self.product, sub_class="product")
        if qs.count()> 0:
            self.query_set = qs
            return
        qs = CropPriceWholesale.objects.filter(name__icontains=self.product, sub_class="product")
        if qs.count() > 5:
            list_product = list(qs.values_list("name", flat=True))
            message = '\n'.join([product for product in list_product])
            self.message = f"品項「{self.product}」有多個搜尋結果，請改用完整關鍵字如下：\n" + message
            raise CustomError(self.message)
        elif qs.count() == 0:
            self.message = f"查無品項「{self.product}」"
            raise CustomError(self.message)
        else:
            self.query_set = qs

    def get_query(self, obj):
        if self.option_selected != obj.main_class:
            # 選擇主分類
            self.option_selected = obj.main_class
            driver_select(self.driver, self.id_group, "text", obj.main_class)
        # 選擇產品
        time.sleep(1)
        driver_select(self.driver, self.id_product, "value", obj.value, True)
        # 送出查詢
        btn_search = self.driver.find_element(By.ID, self.id_search)
        btn_search.click()

    def get_table(self, obj):
        try:
            check_year = self.driver.find_element(By.ID, self.id_check_year)
        except Exception as e:
            check_year = None
        try:
            check_month = self.driver.find_element(By.ID, self.id_check_month)
        except Exception as e:
            check_month = None

        if self.month and check_month is not None:
            if check_year:
                check_year.click()
            try:
                driver_select(self.driver, self.id_start_month, "value", self.select_date)
                driver_select(self.driver, self.id_end_month, "value", self.select_date)
            except Exception as e:
                options = self.driver.find_element(By.ID, self.id_start_month).text.replace(" ", "").replace("年", "/").replace("月", "")
                options = options.split("\n")
                date_start = options[0]
                date_end = options[-1]
                self.result.append(f"{obj.name}：日期超過範圍，請選擇日期於「{date_start}」～「{date_end}」之間")
                raise CustomError()
        elif self.month and check_month is None:
            options = self.driver.find_element(By.ID, self.id_start_year).text.replace(" ", "").replace("年", "")
            options = options.split("\n")
            date_start = options[0]
            date_end = options[-1]
            self.result.append(f"{obj.name}：只有年資料沒有月份資料，請選擇年份「{date_start}」～「{date_end}」之間")
            raise CustomError()
        elif self.month is None and check_year is None:
            options = self.driver.find_element(By.ID, self.id_start_month).text.replace(" ", "").replace("年", "/").replace("月", "")
            options = options.split("\n")
            date_start = options[0]
            date_end = options[-1]
            self.result.append(f"{obj.name}：只有月份資料沒有年資料，請選擇日期於「{date_start}」～「{date_end}」之間")
            raise CustomError()
        else:
            if check_month:
                check_month.click()
            try:
                driver_select(self.driver, self.id_start_year, "value", self.select_date)
                driver_select(self.driver, self.id_end_year, "value", self.select_date)
            except Exception as e:
                options = self.driver.find_element(By.ID, self.id_start_year).text.replace(" ", "").replace("年", "")
                options = options.split("\n")
                date_start = options[0]
                date_end = options[-1]
                self.result.append(f"{obj.name}：年份「{self.query_date}」超出範圍，年份需介於「{date_start}」～「{date_end}」之間")
                raise CustomError()

        btn_query = self.driver.find_element(By.ID, self.id_query)
        btn_query.click()

    def get_result(self, obj):
        WebDriverWait(self.driver, 30, 0.1).until(EC.presence_of_element_located((By.ID, self.id_table)))
        table = self.driver.find_element(By.ID, self.id_table)
        result = self.driver.find_element(By.CSS_SELECTOR, ".VerDim").parent.find_element(By.CSS_SELECTOR, ".ValueLeftTop").text
        unit = self.driver.find_element(By.ID, self.id_table).find_elements(By.TAG_NAME, 'tr')[0].text
        unit = '(' + unit.split('（')[-1].replace('）', '') + ')'
        if '...' in result:
            self.result.append(f"{obj.name}：查無結果")
        else:
            self.result.append(f"{obj.name}：{result}{unit}")

    def get_back(self):
        btn_back = self.driver.find_element(By.ID, self.id_back)
        btn_back.click()

    def get_data(self):
        self.parser()
        self.get_product()
        for obj in self.query_set:
            try:
                self.get_query(obj)
                self.get_table(obj)
                self.get_result(obj)
            except CustomError:
                pass
            self.get_back()
        if self.month:
            self.message = f"{self.year}年{self.month}月 {self.product} 批發：\n" + "\n".join(result for result in self.result)
        else:
            self.message = f"{self.year}年 {self.product} 批發：\n" + "\n".join(result for result in self.result)
