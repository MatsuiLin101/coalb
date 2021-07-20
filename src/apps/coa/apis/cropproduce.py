from .configs import *


class CropProduceApiView(BasicApiView):
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
    def __init__(self, params):
        self.params = params
        self.command = params[0]

    def choose_api(self):
        if self.command in ["產量", "種植面積"]:
            return CropProduceTotalApiView(self.params)
        elif self.command in ["單位產值", "單位產量"]:
            return CropProduceUnitApiView(self.params)


class CropProduceTotalApiView(BasicApiView):
    '''
    農耕作物生產api介面
    -produce(作物生產)
    --(NEW)產量
    農糧署農情報告資源網 https://agr.afa.gov.tw/afa/afa_frame.jsp
    --(NEW)種植面積
    農糧署農情報告資源網 https://agr.afa.gov.tw/afa/afa_frame.jsp
    '''
    def __init__(self, params):
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
        self.message = ""
        self.params = params

        self.command = params[0]
        if len(params) != 4:
            message = f"種植面積的指令為「種植面積 縣市 品項 年份」可加上鄉鎮「種植面積 縣市鄉鎮 品項 年份」，例如：\n"
            message += f"「種植面積 雲林 落花生 108」\n「種植面積 雲林土庫 落花生 108」"
            raise CustomError(message)

        self.city = params[1].replace('台', '臺')
        self.product = params[2]
        self.query_date = params[3]
        if len(self.city) > 2:
            if "市" in self.city or "縣" in self.city:
                self.city, self.district = self.city[:3], self.city[3:]
            else:
                self.city, self.district = self.city[:2], self.city[2:]
        else:
            self.district = ""
        self.command_text = " ".join(text for text in params)

    def get_product(self):
        query_set = CropProduceTotal.objects.filter(name__icontains=self.product)
        if 0 < query_set.count() <= 5:
            return
        elif query_set.count() == 0:
            self.message = f"作物「{self.product}」不在清單中，請修改作物名後重新查詢"
        else:
            self.message = f"搜尋品項「{self.product}」結果過多，請修改作物名後重新查詢"
        raise CustomError(self.message)

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
            raise CustomError(self.message)
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
            raise CustomError(self.message)

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
                raise CustomError(self.message)
            driver_select_xpath(self.driver, self.select_city, "text", self.target_city[0])
        else:
            self.message = f"縣市「{self.city}」不在清單中，請修改縣市名後重新查詢"
            raise CustomError(self.message)

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
                self.message += f"種植面積 {self.year} {self.city}{self.district} {product.split('.')[-1]}：查無資料\n\n"
            elif self.district:
                if self.district in table.text:
                    data_list = table.text.split('\n')
                    for data in data_list:
                        if self.district in data and "縣市鄉鎮" not in data:
                            district = data.split(' ')[0]
                            produce = data.split(' ')[-1]
                            farmerarea = round(float(data.split(' ')[1].replace(',', '')))
                            self.message += f"產量 {self.year} {district} {product.split('.')[-1]}：{produce}(公斤)\n"
                            self.message += f"種植面積 {self.year} {district} {product.split('.')[-1]}：{farmerarea:,d}(公頃)\n\n"
                else:
                    self.message += f"產量 {self.year} {self.city}{self.district} {product.split('.')[-1]}：查無資料\n"
                    self.message += f"種植面積 {self.year} {self.city}{self.district} {product.split('.')[-1]}：查無資料\n\n"
            else:
                produce = table.text.split('\n')[-1].split(' ')[-1]
                farmerarea = round(float(table.text.split('\n')[-1].split(' ')[1].replace(',', '')))
                self.message += f"產量 {self.year} {self.city}{self.district} {product.split('.')[-1]}：{produce}(公斤)\n"
                self.message += f"種植面積 {self.year} {self.city}{self.district} {product.split('.')[-1]}：{farmerarea:,d}(公頃)\n\n"
        self.message = self.message[:-1]

    def get_data(self):
        self.get_product()
        self.parser()
        self.set_query()
        self.get_table()


class CropProduceUnitApiView(BasicApiView):
    '''
    —-單位產值
    EXCEL匯入
    —-單位產量
    EXCEL匯入
    '''
    def __init__(self, params):
        self.params = params
        self.command = params[0]
        self.command_text = " ".join(text for text in params)

        if len(params) != 3:
            if self.command == "單位產值":
                message = f"單位產值的指令為「單位產值 縣市 品項」，也可加上鄉鎮「單位產值 縣市鄉鎮 品項」，例如：\n「單位產值 屏東 香蕉」\n「單位產值 雲林二崙 香蕉」"
            else:
                message = f"單位產量的指令為「單位產量 縣市 品項」，也可加上鄉鎮「單位產量 縣市鄉鎮 品項」，例如：\n「單位產量 屏東 香蕉」\n「單位產量 雲林二崙 香蕉」"
            raise CustomError(message)

        self.city = params[1].replace("台", "臺")
        self.product = params[2]
        if len(self.city) > 2:
            if self.city[2] in ["市", "縣"]:
                self.city, self.district = self.city[:3], self.city[3:]
            else:
                self.city, self.district = self.city[:2], self.city[2:]
        else:
            self.district = None
        self.command_text = " ".join(text for text in params)

    def execute_api(self):
        try:
            self.get_data()
        except Exception as e:
            traceback_log = TracebackLog.objects.create(app=f"{self.classname}", message=traceback.format_exc())
            self.message = f"「{self.command_text}」發生未知錯誤，錯誤編號「{traceback_log.id}」，請通知管理員處理"
        return self.message

    def get_data(self):
        if self.district is None:
            self.query_set = CropProduceUnit.objects.filter(city__icontains=self.city, district=None, name__icontains=self.product)
        else:
            self.query_set = CropProduceUnit.objects.filter(city__icontains=self.city, district__icontains=self.district, name__icontains=self.product)

        list_result = list()
        for obj in self.query_set:
            name = obj.name
            if obj.period is not None:
                name += obj.period
            if self.district is not None:
                district = obj.district
            else:
                district = ""
            amount_max = round(obj.amount_max)
            amount_min = round(obj.amount_min)
            amount_average = round(obj.amount_average)
            amount_unit = obj.amount_unit
            value_max = round(obj.value_max)
            value_min = round(obj.value_min)
            value_average = round(obj.value_average)
            value_unit = obj.value_unit
            result = f"{self.city}{district} {name}\n"
            result += f"平均單位產值：\n平均：{value_average:,d}{value_unit}\n最小值：{value_min:,d}{value_unit}\n最大值：{value_max:,d}{value_unit}\n"
            result += f"平均單位產量：\n平均：{amount_average:,d}{amount_unit}\n最小值：{amount_min:,d}{amount_unit}\n最大值：{amount_max:,d}{amount_unit}"
            list_result.append(result)

        if len(list_result) > 0:
            self.message = "\n\n".join(result for result in list_result)
        else:
            if self.district:
                self.message = f"{self.city}{self.district} {self.product}\n平均單位產值：查無資料\n平均單位產量：查無資料"
            else:
                self.message = f"{self.city} {self.product}\n平均單位產值：查無資料\n平均單位產量：查無資料"
