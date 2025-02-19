from .configs import *


class ProduceValueApiView(BasicApiView):
    '''
    產值api介面
    producevalue(產值)
    -TotalValue(總產值)
    動態查詢 [農業生產統計]>>[農業產值結構與指標]>>[農業產值：縣市別×農業別]
    https://agrstat.moa.gov.tw/sdweb/public/inquiry/InquireAdvance.aspx
    -Value(產值)
    年報一、(四)
    https://agrstat.moa.gov.tw/sdweb/public/book/Book.aspx
    '''
    def __init__(self, params):
        self.params = params
        self.command = params[0]

    def choose_api(self):
        if self.command in ["總產值"]:
            return TotalValueApiView(self.params)
        elif self.command in ["產值"]:
            return ValueApiView(self.params)


class TotalValueApiView(BasicApiView):
    '''
    producevalue(產值)
    -TotalValue(總產值)
    動態查詢 [農業生產統計]>>[農業產值結構與指標]>>[農業產值：縣市別×農業別]
    https://agrstat.moa.gov.tw/sdweb/public/inquiry/InquireAdvance.aspx
    '''
    def __init__(self, params):
        self.driver = None
        self.url = "https://agrstat.moa.gov.tw/sdweb/public/inquiry/InquireAdvance.aspx"
        self.text_title = "農業產值結構與指標"
        self.text_group = "農業產值：縣市別×農業別"
        self.id_group = "ctl00_cphMain_uctlInquireAdvance_lstFieldGroup"
        self.id_city = "ctl00_cphMain_uctlInquireAdvance_dtlDimension_ctl00_lstDimension"
        self.id_category = "ctl00_cphMain_uctlInquireAdvance_dtlDimension_ctl02_lstDimension"
        self.id_search = "ctl00_cphMain_uctlInquireAdvance_btnQuery"
        self.id_start_year = "ctl00_cphMain_uctlInquireAdvance_ddlYearBegin"
        self.id_end_year = "ctl00_cphMain_uctlInquireAdvance_ddlYearEnd"
        self.id_query = "ctl00_cphMain_uctlInquireAdvance_btnQuery2"
        self.id_table = "ctl00_cphMain_uctlInquireAdvance_tabResult"
        self.id_back = "ctl00_cphMain_uctlInquireAdvance_btnBack2"
        self.message = ""
        self.params = params

        if not 2 <= len(params) <= 3:
            raise CustomError(f"總產值的指令為「總產值 年份」或可加上城市「總產值 城市 年份」，例如：\n「總產值 107」\n「總產值 台中 108」")
        self.command = params[0]
        if len(params) == 2:
            self.city = None
            self.query_date = params[1]
        else:
            self.city = params[1].replace('台', '臺')
            self.query_date = params[2]
        self.command_text = " ".join(text for text in params)

    def parser(self):
        super(TotalValueApiView, self).parser()
        # 進入畜禽產品飼養數量統計頁面
        self.driver.find_element(By.LINK_TEXT, self.text_title).click()

    def get_city(self):
        # 是否有完全符合name的物件
        try:
            self.obj_city = TotalValue.objects.get(name=self.city, sub_class="city")
            return
        except Exception as e:
            pass

        # 是否有部分符合name的物件
        try:
            self.obj_city = TotalValue.objects.get(name__icontains=self.city, sub_class="city")
            return
        except Exception as e:
            pass

        # 是否有完全符合search_name的物件
        try:
            self.obj_city = TotalValue.objects.get(search_name=self.city, sub_class="city")
            return
        except Exception as e:
            pass

        # 可能有多種結果，請使用者改用詳細關鍵字
        qs = TotalValue.objects.filter(name__icontains=self.city, sub_class="city")
        if qs.count() > 0:
            list_city = list(qs.values_list("search_name", flat=True))
            message = '\n'.join([city for city in list_city])
            self.message = f"城市「{self.city}」有多個搜尋結果，請改用完整關鍵字如下：\n" + message
        else:
            self.message = f"查無城市「{self.city}」"
        raise CustomError(self.message)

    def get_query(self):
        driver_select(self.driver, self.id_group, "text", self.text_group)
        # 選擇城市
        if self.city is not None:
            time.sleep(0.5)
            driver_select(self.driver, self.id_city, "value", self.obj_city.value, True)
        # 選擇全部農業別
        time.sleep(0.5)
        qs_category = TotalValue.objects.filter(sub_class="category")
        for obj in qs_category:
            driver_select(self.driver, self.id_category, "value", obj.value)
        # 送出查詢
        btn_search = self.driver.find_element(By.ID, self.id_search)
        btn_search.click()

    def get_result(self):
        WebDriverWait(self.driver, 30, 0.1).until(EC.presence_of_element_located((By.ID, self.id_table)))
        table = self.driver.find_element(By.ID, self.id_table)
        self.result_1 = self.driver.find_element(By.CSS_SELECTOR, ".VerDim").parent.find_element(By.CSS_SELECTOR, ".ValueLeftTop").text
        self.result_2 = self.driver.find_element(By.CSS_SELECTOR, ".VerDim").parent.find_elements(By.CSS_SELECTOR, ".ValueTop")[0].text
        self.result_3 = self.driver.find_element(By.CSS_SELECTOR, ".VerDim").parent.find_elements(By.CSS_SELECTOR, ".ValueTop")[1].text
        self.result_4 = self.driver.find_element(By.CSS_SELECTOR, ".VerDim").parent.find_elements(By.CSS_SELECTOR, ".ValueTop")[2].text
        self.result_5 = self.driver.find_element(By.CSS_SELECTOR, ".VerDim").parent.find_elements(By.CSS_SELECTOR, ".ValueTop")[3].text

    def get_data(self):
        self.parser()
        if self.city is not None:
            self.get_city()
        self.get_query()
        self.get_table()
        self.get_result()


        if self.city is not None:
            self.message = f"{self.year}年 {self.obj_city.name} 總產值：\n" + f"農業：{self.result_1}(千元)\n" + f"農產：{self.result_2}(千元)\n" + f"林產：{self.result_3}(千元)\n" + f"畜產：{self.result_4}(千元)\n" + f"漁產：{self.result_5}(千元)"
        else:
            self.message = f"{self.year}年 總產值：\n" + f"農業：{self.result_1}(千元)\n" + f"農產：{self.result_2}(千元)\n" + f"林產：{self.result_3}(千元)\n" + f"畜產：{self.result_4}(千元)\n" + f"漁產：{self.result_5}(千元)"



class ValueApiView(AnnualReportBasicApiView):
    '''
    -Value(產值)
    年報一、(四)
    https://agrstat.moa.gov.tw/sdweb/public/book/Book.aspx
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
