from .configs import *


class CropCostApiView(BasicApiView):
    '''
    農耕生產成本api介面
    -cost(生產成本)
    --生產成本
    同時查詢生產費用、粗收益、淨收入率、工時
    —-生產費用
    動態查詢 [農業生產統計]>>[農畜產品生產成本統計]>> [農產品每公頃生產費用：每公頃生產費用×生產費用與收益_農產品項目]>>[生產費用總計]
    https://agrstat.moa.gov.tw/sdweb/public/inquiry/InquireAdvance.aspx
    —-粗收益
    動態查詢 [農業生產統計]>>[農畜產品生產成本統計]>>  [農產品每公頃生產量與收益：每公頃生產量與收益×生產費用與收益_農產品項目]>>[粗收益]
    https://agrstat.moa.gov.tw/sdweb/public/inquiry/InquireAdvance.aspx
    —-淨收入率
    動態查詢
    https://agrstat.moa.gov.tw/sdweb/public/inquiry/InquireAdvance.aspx
    —-工時
    動態查詢 [農業生產統計]>>[農畜產品生產成本統計]>>[農產品每公頃人工時數(小時)：人工時數×生產費用與收益_農產品項目]>>[男工＋女工]合計
    https://agrstat.moa.gov.tw/sdweb/public/inquiry/InquireAdvance.aspx
    '''
    def __init__(self, params):
        self.driver = None
        self.url = "https://agrstat.moa.gov.tw/sdweb/public/inquiry/InquireAdvance.aspx"
        self.text_title = "農畜產品生產成本統計"
        self.text_group1 = "農產品每公頃生產費用：每公頃生產費用×生產費用與收益_農產品項目"
        self.text_group2 = "農產品每公頃生產量與收益：每公頃生產量與收益×生產費用與收益_農產品項目"
        self.text_group3 = "農產品每公頃人工時數(小時)：人工時數×生產費用與收益_農產品項目"
        self.id_group = "ctl00_cphMain_uctlInquireAdvance_lstFieldGroup"
        self.id_category = "ctl00_cphMain_uctlInquireAdvance_dtlDimension_ctl00_lstDimension"
        self.id_product = "ctl00_cphMain_uctlInquireAdvance_dtlDimension_ctl02_lstDimension"
        self.id_search = "ctl00_cphMain_uctlInquireAdvance_btnQuery"
        self.id_check_year = "ctl00_cphMain_uctlInquireAdvance_chkYear"
        self.id_start_year = "ctl00_cphMain_uctlInquireAdvance_ddlYearBegin"
        self.id_end_year = "ctl00_cphMain_uctlInquireAdvance_ddlYearEnd"
        self.id_query = "ctl00_cphMain_uctlInquireAdvance_btnQuery2"
        self.id_table = "ctl00_cphMain_uctlInquireAdvance_tabResult"
        self.id_back = "ctl00_cphMain_uctlInquireAdvance_btnBack2"
        self.message = ""
        self.params = params

        if len(params) != 3:
            raise CustomError(f"生產成本(生產費用、粗收益、淨收入率、工時)的指令為「成本 作物 年份」，例如：\n「成本 香蕉 107」\n\n也可單獨查詢，例如：\n「生產費用 香蕉 107」\n「粗收益 香蕉 107」\n「淨收入率 香蕉 107」\n「工時 香蕉 107」")
        self.command = params[0]
        self.product = params[1]
        self.query_date = params[2]
        self.command_text = " ".join(text for text in params)

    def choose_api(self):
        if self.command in ["成本", "生產成本"]:
            return TotalCost(self.params)
        elif self.command in ["費用", "生產費用"]:
            return ProduceCost(self.params)
        elif self.command in ["粗收益"]:
            return CrudeIncome(self.params)
        elif self.command in ["淨收入率"]:
            return PureIncomeRate(self.params)
        elif self.command in ["工時"]:
            return WorkHour(self.params)

    def parser(self):
        super(CropCostApiView, self).parser()
        # 進入農畜產品生產成本統計頁面
        self.driver.find_element(By.LINK_TEXT, self.text_title).click()

    def get_product(self):
        # 根據使用者輸入的product選擇對應的group
        # 是否有完全符合name的物件
        try:
            self.obj_product = CropCost.objects.get(name=self.product, main_class=self.text_group, sub_class="product")
            return
        except Exception as e:
            pass

        # 是否有部分符合name的物件
        try:
            self.obj_product = CropCost.objects.get(name__icontains=self.product, main_class=self.text_group, sub_class="product")
            return
        except Exception as e:
            pass

        # 是否有完全符合search_name的物件
        try:
            self.obj_product = CropCost.objects.get(search_name=self.product, main_class=self.text_group, sub_class="product")
            return
        except Exception as e:
            pass

        # 可能有多種結果，請使用者改用詳細關鍵字
        qs = CropCost.objects.filter(name__icontains=self.product, main_class=self.text_group, sub_class="product")
        if qs.count() > 0:
            list_product = list(qs.values('name', 'start_year', 'end_year'))
            message = '\n'.join([f"{product['name']}　年份({product['start_year']}～{product['end_year']})" for product in list_product])
            self.message = f"品項「{self.product}」有多個搜尋結果，請改用完整關鍵字如下：\n" + message
        else:
            self.message = f"查無品項「{self.product}」"
        raise CustomError(self.message)

    def get_query(self):
        driver_select(self.driver, self.id_group, "text", self.text_group)
        # 選擇複分類
        time.sleep(0.5)
        driver_select(self.driver, self.id_category, "text", self.text_category, True)
        # 選擇產品
        time.sleep(0.5)
        driver_select(self.driver, self.id_product, "value", self.obj_product.value, True)
        # 送出查詢
        btn_search = self.driver.find_element(By.ID, self.id_search)
        btn_search.click()

    def get_table(self):
        try:
            super().get_table()
        except Exception as e:
            self.message = str(e)
            qs = CropCost.objects.filter(name__icontains=self.product, main_class=self.text_group, sub_class="product")
            if qs.count() > 1:
                list_product = list(qs.values('name', 'start_year', 'end_year'))
                message = '\n'.join([f"{product['name']}　年份({product['start_year']}～{product['end_year']})" for product in list_product])
                self.message += f"\n\n有其他相似的品項如下：\n" + message
            raise CustomError(self.message)


    def get_result(self):
        WebDriverWait(self.driver, 30, 0.1).until(EC.presence_of_element_located((By.ID, self.id_table)))
        table = self.driver.find_element(By.ID, self.id_table)
        self.result = self.driver.find_element(By.CSS_SELECTOR, ".VerDim").parent.find_element(By.CSS_SELECTOR, ".ValueLeftTop").text

    def re_query(self):
        btn_back = self.driver.find_element(By.ID, self.id_back)
        btn_back.click()

    def get_data(self):
        self.parser()
        self.get_product()
        self.get_query()
        self.get_table()
        self.get_result()

        self.message = f"{self.year}年 {self.obj_product.name} {self.command}：{self.result}{self.unit}"


class TotalCost(CropCostApiView):
    '''
    生產成本api介面
    '''
    def __init__(self, params):
        super(TotalCost, self).__init__(params)
        self.text_group1 = "農產品每公頃生產費用：每公頃生產費用×生產費用與收益_農產品項目"
        self.text_category1 = "生產費用總計"
        self.text_group2 = "農產品每公頃生產量與收益：每公頃生產量與收益×生產費用與收益_農產品項目"
        self.text_category2 = "粗收益"
        self.text_group4 = "農產品每公頃人工時數(小時)：人工時數×生產費用與收益_農產品項目"
        self.text_category41 = "男工"
        self.text_category42 = "女工"
        self.unit1 = "(元/公頃)"
        self.unit2 = "(元/公頃)"
        self.unit3 = "(%)"
        self.unit4 = "(小時/公頃)"

    def get_produce_cost(self):
        # 取得生產費用
        self.text_group = self.text_group1
        self.text_category = self.text_category1
        self.parser()
        self.get_product()
        self.get_query()
        self.get_table()
        self.get_result()
        self.result_a = self.result

    def get_crude_income(self):
        # 取得粗收益
        self.re_query()
        self.text_group = self.text_group2
        self.text_category = self.text_category2
        self.get_query()
        self.get_table()
        self.get_result()
        self.result_b = self.result

    def get_work_hour(self):
        # 取得工時
        self.re_query()
        self.text_group = self.text_group4

        # get_query
        # 選擇主分類
        driver_select(self.driver, self.id_group, "text", self.text_group)
        # 選擇複分類
        time.sleep(0.5)
        driver_select(self.driver, self.id_category, "text", self.text_category41)
        driver_select(self.driver, self.id_category, "text", self.text_category42)
        # 選擇產品
        time.sleep(0.5)
        driver_select(self.driver, self.id_product, "value", self.obj_product.value, True)
        # 送出查詢
        btn_search = self.driver.find_element(By.ID, self.id_search)
        btn_search.click()

        self.get_table()

        # get_result()
        WebDriverWait(self.driver, 30, 0.1).until(EC.presence_of_element_located((By.ID, self.id_table)))
        table = self.driver.find_element(By.ID, self.id_table)
        self.result_male = self.driver.find_element(By.CSS_SELECTOR, ".VerDim").parent.find_element(By.CSS_SELECTOR, ".ValueLeftTop").text.replace(',', '')
        self.result_female = self.driver.find_element(By.CSS_SELECTOR, ".VerDim").parent.find_element(By.CSS_SELECTOR, ".ValueTop").text.replace(',', '')
        try:
            self.result_d = f"{round(float(self.result_male) + float(self.result_female))}{self.unit4}"
        except Exception as e:
            self.result_d = f"無法計算，男工：{self.result_male}、女工：{self.result_female}"


    def calc_income_rate(self):
        self.result_a = round(float(self.result_a.replace(',', '')))
        self.result_b = round(float(self.result_b.replace(',', '')))
        self.result_c = round((self.result_b - self.result_a) / self.result_b * 100)

    def get_data(self):
        self.get_produce_cost()
        self.get_crude_income()
        self.get_work_hour()

        self.calc_income_rate()
        self.message = f"{self.year}年 {self.obj_product.name} {self.command}：\n"
        self.message += f"生產費用：{self.result_a:,d}{self.unit1}\n"
        self.message += f"粗收益：{self.result_b:,d}{self.unit2}\n"
        self.message += f"淨收入率：{self.result_c:,d}{self.unit3}\n"
        self.message += f"工時：{self.result_d}\n"


class ProduceCost(CropCostApiView):
    '''
    生產費用api介面
    '''
    def __init__(self, params):
        super(ProduceCost, self).__init__(params)
        self.text_group = "農產品每公頃生產費用：每公頃生產費用×生產費用與收益_農產品項目"
        self.text_category = "生產費用總計"
        self.unit = "(元/公頃)"


class CrudeIncome(CropCostApiView):
    '''
    粗收益api介面
    '''
    def __init__(self, params):
        super(CrudeIncome, self).__init__(params)
        self.text_group = "農產品每公頃生產量與收益：每公頃生產量與收益×生產費用與收益_農產品項目"
        self.text_category = "粗收益"
        self.unit = "(元/公頃)"


class PureIncomeRate(CropCostApiView):
    '''
    淨收入率api介面
    '''
    def __init__(self, params):
        super(PureIncomeRate, self).__init__(params)
        self.text_group1 = "農產品每公頃生產費用：每公頃生產費用×生產費用與收益_農產品項目"
        self.text_category1 = "生產費用總計"
        self.text_group2 = "農產品每公頃生產量與收益：每公頃生產量與收益×生產費用與收益_農產品項目"
        self.text_category2 = "粗收益"
        self.unit = "(%)"

    def calc_result(self):
        self.result_a = round(float(self.result_a.replace(',', '')))
        self.result_b = round(float(self.result_b.replace(',', '')))
        self.result = round((self.result_b - self.result_a) / self.result_b * 100)

    def get_data(self):
        self.text_group = self.text_group1
        self.text_category = self.text_category1
        self.parser()
        self.get_product()
        self.get_query()
        self.get_table()
        self.get_result()
        self.result_a = self.result
        self.re_query()
        self.text_group = self.text_group2
        self.text_category = self.text_category2
        self.get_product()
        self.get_query()
        self.get_table()
        self.get_result()
        self.result_b = self.result
        self.calc_result()
        self.message = f"{self.year}年 {self.obj_product.name} {self.command}：{self.result}{self.unit}"


class WorkHour(CropCostApiView):
    '''
    工時api介面
    '''
    def __init__(self, oarams):
        super(WorkHour, self).__init__(oarams)
        self.text_group = "農產品每公頃人工時數(小時)：人工時數×生產費用與收益_農產品項目"
        self.text_category1 = "男工"
        self.text_category2 = "女工"
        self.unit = "(小時/公頃)"

    def get_query(self):
        driver_select(self.driver, self.id_group, "text", self.text_group)
        # 選擇複分類
        time.sleep(0.5)
        driver_select(self.driver, self.id_category, "text", self.text_category1)
        driver_select(self.driver, self.id_category, "text", self.text_category2)
        # 選擇產品
        time.sleep(0.5)
        driver_select(self.driver, self.id_product, "value", self.obj_product.value, True)
        # 送出查詢
        btn_search = self.driver.find_element(By.ID, self.id_search)
        btn_search.click()

    def get_result(self):
        WebDriverWait(self.driver, 30, 0.1).until(EC.presence_of_element_located((By.ID, self.id_table)))
        table = self.driver.find_element(By.ID, self.id_table)
        self.result_male = self.driver.find_element(By.CSS_SELECTOR, ".VerDim").parent.find_element(By.CSS_SELECTOR, ".ValueLeftTop").text
        self.result_female = self.driver.find_element(By.CSS_SELECTOR, ".VerDim").parent.find_element(By.CSS_SELECTOR, ".ValueTop").text
        try:
            self.result = round(float(self.result_male) + float(self.result_female))
        except Exception as e:
            self.message = f"{self.year}年 {self.obj_product.name} {self.command}：\n男工：{self.result_male}{self.unit}\n女工：{self.result_female}{self.unit}"
