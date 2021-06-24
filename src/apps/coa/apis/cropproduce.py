from .configs import *


class CropProduceApiView(ApiView):
    '''
    農耕作物生產api介面
    -produce(作物生產)
    --(NEW)產量
    農糧署農情報告資源網 https://agr.afa.gov.tw/afa/afa_frame.jsp
    --(NEW)種植面積
    農糧署農情報告資源網 https://agr.afa.gov.tw/afa/afa_frame.jsp
    —-單位產值
    EXCEL匯入
    —-單位產量
    EXCEL匯入
    '''
    def __init__(self, command, query_date, city, product):
        self.driver = None
        self.url = "https://agr.afa.gov.tw/afa/afa_frame.jsp"
        self.frame_left = "/html/frameset/frameset/frame[1]"
        self.frame_right = "/html/frameset/frameset/frame[2]"
        self.menu1 = "/html/body/div/div/div[1]/a"
        self.menu2 = "/html/body/div/div/div[2]/a"
        self.menu3 = "/html/body/div/div/div[3]/a"
        self.select_year = "/html/body/div/form/div/table/tbody/tr[1]/td[2]/select"
        self.select_product = "/html/body/div/form/div/table/tbody/tr[3]/td[2]/select"
        self.select_city = "/html/body/div/form/div/table/tbody/tr[4]/td[2]/select"
        self.btn_query = "/html/body/div/form/div/table/tbody/tr[5]/td[2]/input[1]"
        self.table = "/html/body/div/form/div/table"
        self.command = command
        self.query_date = query_date
        self.city = city.replace("台", "臺")
        self.district = ""
        self.product = product
        self.message = ""

        if len(self.city) > 3:
            if "市" in self.city or "縣" in self.city:
                self.city, self.district = self.city[:3], self.city[3:]
            else:
                self.city, self.district = self.city[:2], self.city[2:]

    def api(self):
        try:
            self.verify_date()
            if not self.message:
                self.get_data()
        except Exception as e:
            traceback_log = TracebackLog.objects.create(app='CropProduceApiView', message=traceback.format_exc())
            if not self.message:
                self.message = f"搜尋「{self.command} {self.query_date} {self.product}」發生錯誤，錯誤編號「{traceback_log.id}」\n"
        if self.driver:
            self.driver.close()
        return self.message

    def verify_date(self):
        # check years
        # 檢查年份是否為數字
        try:
            self.year = int(self.query_date)
        except Exception as e:
            self.message = f"年份「{self.year}」無效，請輸入民國年"
            return

    def parser(self):
        self.driver = get_driver()
        self.driver.get(self.url)

    def set_query(self):
        # switch frame
        frame_left = self.driver.find_element(By.XPATH, self.frame_left)
        frame_right = self.driver.find_element(By.XPATH, self.frame_right)
        self.driver.switch_to_frame(frame_left)
        self.driver.find_element(By.XPATH, self.menu1).click()
        self.driver.find_element(By.XPATH, self.menu2).click()
        self.driver.find_element(By.XPATH, self.menu3).click()
        self.driver.switch_to_default_content()
        self.driver.switch_to_frame(frame_right)

        # set query
        # select year
        select_year = self.driver.find_element(By.XPATH, self.select_year)
        if not str(self.year).zfill(3) in select_year.text:
            range_year = select_year.text.replace(' ', '')
            if range_year.endswith('\n'):
                range_year = range_year[:-1]
            range_year = range_year.split('\n')
            self.message = f"年份「{self.year}」必需在「{int(range_year[-1])}」到「{int(range_year[0])}」之間"
            return
        driver_select_xpath(self.driver, self.select_year, "value", str(self.year).zfill(3))

        # select product
        select_product = self.driver.find_element(By.XPATH, self.select_product)
        if self.product in select_product.text:
            self.target_product = list()
            for product in select_product.text.replace(' ', '')[:-1].split('\n'):
                if self.product in product:
                    self.target_product.append(product)
        else:
            self.message = f"作物「{self.product}」不在清單中，請修改作物名後重新查詢"
            return

        # select city
        select_city = self.driver.find_element(By.XPATH, self.select_city)
        if self.city in select_city.text:
            self.target_city = list()
            for city in select_city.text.replace(' ', '')[:-1].split('\n'):
                if self.city in city:
                    self.target_city.append(city)
            if len(self.target_city) != 1:
                self.message = f"縣市「{self.city}」有{len(self.target_city)}種結果，請輸入準確的縣市名稱\n"
                for target in self.target_city:
                    self.message += f"{target.split('.')[-1]}\n"
                self.message = self.message[:-1]
                return
            driver_select_xpath(self.driver, self.select_city, "text", self.target_city[0])
        else:
            self.message = f"縣市「{self.city}」不在清單中，請修改縣市名後重新查詢"
            return

    def get_table(self):
        self.list_result = list()
        for product in self.target_product:
            # reload page to avoid element locate error
            self.driver.get(self.url)
            frame_left = self.driver.find_element(By.XPATH, self.frame_left)
            frame_right = self.driver.find_element(By.XPATH, self.frame_right)
            self.driver.switch_to_frame(frame_left)
            self.driver.find_element(By.XPATH, self.menu1).click()
            self.driver.find_element(By.XPATH, self.menu2).click()
            self.driver.find_element(By.XPATH, self.menu3).click()
            self.driver.switch_to_default_content()
            self.driver.switch_to_frame(frame_right)
            select_year = self.driver.find_element(By.XPATH, self.select_year)
            driver_select_xpath(self.driver, self.select_year, "value", str(self.year).zfill(3))
            select_city = self.driver.find_element(By.XPATH, self.select_city)
            driver_select_xpath(self.driver, self.select_city, "text", self.target_city[0])

            # send query
            driver_select_xpath(self.driver, self.select_product, "text", product)
            btn_query = self.driver.find_element(By.XPATH, self.btn_query)
            btn_query.click()

            # get data
            table = self.driver.find_element(By.XPATH, self.table)
            if "查無資料" in table.text:
                self.message += f"產量 {self.year} {self.city}{self.district} {product.split('.')[-1]}：查無資料\n"
                self.message += f"種植面積 {self.year} {self.city}{self.district} {product.split('.')[-1]}：查無資料\n"
            elif self.district:
                if self.district in table.text:
                    data_list = table.text.split('\n')
                    for data in data_list:
                        if self.district in data:
                            district = data.split(' ')[0]
                            produce = data.split(' ')[-1]
                            farmerarea = round(float(data.split(' ')[1].replace(',', '')))
                            self.message += f"產量 {self.year} {district} {product.split('.')[-1]}：{produce}(公斤)\n"
                            self.message += f"種植面積 {self.year} {district} {product.split('.')[-1]}：{farmerarea:,d}(公頃)\n"
                else:
                    self.message += f"產量 {self.year} {self.city}{self.district} {product.split('.')[-1]}：查無資料\n"
                    self.message += f"種植面積 {self.year} {self.city}{self.district} {product.split('.')[-1]}：查無資料\n"
            else:
                produce = table.text.split('\n')[-1].split(' ')[-1]
                farmerarea = round(float(table.text.split('\n')[-1].split(' ')[1].replace(',', '')))
                self.message += f"產量 {self.year} {self.city}{self.district} {product.split('.')[-1]}：{produce}(公斤)\n"
                self.message += f"種植面積 {self.year} {self.city}{self.district} {product.split('.')[-1]}：{farmerarea:,d}(公頃)\n"
        self.message = self.message[:-1]

    def get_data(self):
        self.parser()
        self.set_query()
        if self.message:
            return
        self.get_table()
