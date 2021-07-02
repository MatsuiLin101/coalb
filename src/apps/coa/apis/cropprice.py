from .configs import *


class CropPriceApiView(ApiView):
    '''
    農耕價格api介面
    -price(價格)
    -—產地價
    農糧署農產品產地價格查報系統
    https://apis.afa.gov.tw/pagepub/AppContentPage.aspx?itemNo=PRI105
    —-批發價
    動態查詢 [農產品運銷統計]>>[農產品價格統計]>>[蔬菜批發價格：蔬菜別]、[果品批發價格：果品別]、[白米批發(躉售)價格：稻種別]
    https://agrstat.coa.gov.tw/sdweb/public/inquiry/InquireAdvance.aspx
from apps.coa.apis.cropprice import *
a = CropPriceApiView('aaa', '108/6', '芒果')
    '''
    def __init__(self, command, query_date, product, city=None):
        self.driver = None
        self.url = "https://apis.afa.gov.tw/pagepub/AppContentPage.aspx?itemNo=PRI105"
        self.id_radio_month = "WR1_1_Q_AvgPriceType_C1_1"
        self.id_select_year_start = "WR1_1_Q_PRSR_Year1_C1"
        self.id_select_year_end = "WR1_1_Q_PRSR_Year2_C1"
        self.id_select_month_start = "WR1_1_Q_PRSR_Month1_C1"
        self.id_select_month_end = "WR1_1_Q_PRSR_Month2_C1"
        self.id_category = "WR1_1_Q_GroupCode_XX_C1"
        self.id_result_table = "WR1_1_WG1"
        self.command = command
        self.query_date = str(query_date)
        self.product = product
        self.city = city
        self.year = ""
        self.month = ""
        self.result = list()
        self.message = ""
        self.start_time = datetime.datetime.now()

        if city:
            self.city = self.city.replace("臺", "台")

    def api(self):
        try:
            self.verify_date()
            if not self.message:
                self.get_data()
        except Exception as e:
            print(traceback.format_exc())
            traceback_log = TracebackLog.objects.create(app='CropPriceApiView', message=traceback.format_exc())
            if not self.message:
                self.message = f"搜尋「{self.command} {self.query_date} {self.product}」發生錯誤，錯誤編號「{traceback_log.id}」\n"
        if self.driver:
            self.driver.close()
        return self.message

    def verify_date(self):
        # check years
        # 檢查年份是否為數字
        if '/' in self.query_date:
            self.year, self.month = self.query_date.split('/')
        else:
            self.year = self.query_date
        try:
            self.year = int(self.year)
            self.query_date = f"{self.year}年"
        except Exception as e:
            self.message = f"年份「{self.year}」無效，請輸入民國年"
        if self.month:
            try:
                self.month = int(self.month)
                if not 1 <= self.month <= 12:
                    self.message = f"月份「{self.month}」請輸入1~12"
                self.query_date += f"{self.month}月"
            except Exception as e:
                self.message = f"月份「{self.month}」無效，請輸入民國年"

    def parser(self):
        self.driver = get_driver()
        self.driver.get(self.url)

    def get_product(self):
        qs = CropPrice.objects.filter(name__icontains=self.product)
        if qs.count() == 0:
            self.message = f"查無品項「{self.product}」"
            return
        elif qs.count() > 5:
            self.message = f"搜尋品項「{self.product}」結果過多，請修改關鍵字後重新查詢：\n" + "\n".join(obj.name for obj in qs)
            return
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
            raise

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
        if self.message:
            return
        self.set_query()
        for obj in self.query_set:
            self.get_query(obj)
            result = self.get_result()
            self.result.append((obj, result))
        self.calc_result()
        if self.city:
            self.message = f"搜尋「{self.command} {self.query_date} {self.product} {self.city}」的結果為：\n"
            product = None
            for result in self.list_result:
                if product != result[0]:
                    product = result[0]
                    self.message += f"{product}\n"
                self.message += f"{result[1]}\n"
            self.message = self.message[:-1]
        else:
            self.message = f"搜尋「{self.command} {self.query_date} {self.product}」的結果為：\n" + "\n".join(result for result in self.list_result)

        self.end_time = datetime.datetime.now()
        self.exe_time = self.end_time - self.start_time

    def close(self):
        self.driver.close()
