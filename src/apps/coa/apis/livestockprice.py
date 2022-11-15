from .configs import *


class LivestockPriceApiView(BasicApiView):
    '''
    其他畜禽價格api介面
    -sale(拍賣價)
    -origin(產地價)
    -retail(零售價)
    畜產品價格查詢系統(舊) http://price.naif.org.tw/Query/Query_now.aspx
    畜產品價格查詢系統(新, 20221114) http://price.naif.org.tw/Query/QueryNow.aspx
    '''
    def __init__(self, params):
        self.driver = None
        self.url = "http://price.naif.org.tw/Query/QueryNow.aspx"
        self.radio_year = '//*[@id="hldContent_rblQDateType"]/label[1]'
        self.select_year_start_year = "hldContent_uctlQBeginPeriod_ddlYear"
        self.select_year_end_year = "hldContent_uctlQEndPeriod_ddlYear"
        self.radio_month = '//*[@id="hldContent_rblQDateType"]/label[2]'
        self.select_month_start_year = "hldContent_uctlQBeginPeriod_ddlYear"
        self.select_month_end_year = "hldContent_uctlQEndPeriod_ddlYear"
        self.select_month_start_month = "hldContent_uctlQBeginPeriod_ddlMonth"
        self.select_month_end_month = "hldContent_uctlQEndPeriod_ddlMonth"
        self.list_product = "ProductMainKind"
        self.btn_query = "hldContent_btnQuery"
        self.btn_selection = "btnShowSelection"
        self.table_nodata = "hldContent_uctlChart_divNoData"
        self.table_report = "hldContent_uctlChart_tabReport"
        self.unit = {
            '鹿茸': '(元/兩)',
            '豬心': '(元/個)',
            '豬腎': '(元/副)',
        }
        self.xpath_report = "/html/body/form/div[4]/div[6]/div/div[2]/div[3]/div[3]/table/tbody/tr[4]/td[2]"
        self.message = ""
        self.year = ""
        self.month = ""
        self.params = params
        self.command = params[0]
        self.command_text = " ".join(text for text in params)

    def choose_api(self):
        if self.command == "拍賣價":
            return Sale(self.params)
        elif self.command == "產地價":
            return Origin(self.params)
        elif self.command == "零售價":
            return Retail(self.params)

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

    def set_date(self):
        if self.month:
            radio_month = self.driver.find_element(By.XPATH, self.radio_month)
            radio_month.click()
            time.sleep(1)
            select_year = self.driver.find_element(By.ID, self.select_month_start_year)
            if not str(self.year - 1911) in select_year.text:
                range_year = select_year.text.replace(' ', '').split('\n')
                self.message = f"年份「{self.year - 1911}」必需在「{int(range_year[0])}」到「{int(range_year[-1])}」之間"
                raise CustomError(self.message)
            driver_select(self.driver, self.select_month_start_year, "value", str(self.year))
            driver_select(self.driver, self.select_month_start_month, "value", str(self.month))
            driver_select(self.driver, self.select_month_end_year, "value", str(self.year))
            driver_select(self.driver, self.select_month_end_month, "value", str(self.month))
        else:
            # radio_year = self.driver.find_element(By.XPATH, self.radio_year)
            # radio_year.click()
            # time.sleep(1)
            select_year = self.driver.find_element(By.ID, self.select_year_start_year)
            if not str(self.year - 1911) in select_year.text:
                range_year = select_year.text.replace(' ', '').split('\n')
                self.message = f"年份「{self.year - 1911}」必需在「{int(range_year[0])}」到「{int(range_year[-1])}」之間"
                raise CustomError(self.message)
            driver_select(self.driver, self.select_year_start_year, "value", str(self.year))
            driver_select(self.driver, self.select_year_end_year, "value", str(self.year))

    def get_table(self):
        check_type = self.driver.find_element(By.ID, self.check_type)
        check_type.click()
        time.sleep(1)
        elements = self.driver.find_elements(By.CLASS_NAME, self.list_product)
        products = "\n".join(element.text for element in elements)
        products = self.filter_products(products)
        targets = list(filter(lambda product: self.product in product, products))

        if len(targets) == 0:
            self.list_result = None
            self.products = products
        else:
            list_result = list()
            for target in targets:
                check_product = self.driver.find_element(By.XPATH, f"//*[contains(text(), '{target}')]")
                check_product.click()
                time.sleep(1)
                btn_query = self.driver.find_element(By.ID, self.btn_query)
                btn_query.click()
                time.sleep(1)
                table_nodata = self.driver.find_element(By.ID, self.table_nodata)
                table_report = self.driver.find_element(By.ID, self.table_report)
                if "查無資料" in table_nodata.text:
                    list_result.append(f"{target} 查無資料")
                else:
                    data = self.driver.find_element(By.XPATH, self.xpath_report)
                    unit = self.unit.get(target) if self.unit.get(target) else '(元/公斤)'
                    list_result.append(f"{target}：{data.text}{unit}")

                btn_selection = self.driver.find_element(By.ID, self.btn_selection)
                btn_selection.click()
                check_product = self.driver.find_element(By.XPATH, f"//*[contains(text(), '{target}')]")
                check_product.click()
            self.list_result = list_result

    def get_data(self):
        self.parser()
        self.set_date()
        self.get_table()
        if self.list_result:
            if self.month:
                self.message = f"{self.year - 1911}年{self.month}月 {self.product} {self.command}：\n"
            else:
                self.message = f"{self.year - 1911}年 {self.product} {self.command}：\n"
            self.message += "\n".join(f"{result}" for result in self.list_result)
        else:
            self.message = f"找不到品項「{self.product}」，可使用的品項如下：\n" + "、".join(product for product in self.products)


class Sale(LivestockPriceApiView):
    '''
    拍賣價api介面
    '''
    def __init__(self, params):
        super(Sale, self).__init__(params)
        self.check_type = "hldContent_rptPriceType_chkPriceType_1"

        if not len(params) == 3:
            raise CustomError(f"{self.command}的指令為「{self.command} 品項 年份」或「{self.command} 品項 年份/月份」，例如：\n「{self.command} 羊 108」\n「{self.command} 羊 108/12」")
        self.product = params[1]
        self.query_date = params[2]

    def filter_products(self, products):
        return products.replace('家畜類\n', '').replace('豬\n', '').replace('羊\n', '').replace(' ', '\n').split('\n')


class Origin(LivestockPriceApiView):
    '''
    產地價api介面
    '''
    def __init__(self, params):
        super(Origin, self).__init__(params)
        self.check_type = "hldContent_rptPriceType_chkPriceType_0"

        if not len(params) == 3:
            raise CustomError(f"{self.command}的指令為「{self.command} 品項 年份」或「{self.command} 品項 年份/月份」，例如：\n「{self.command} 白肉雞 108」\n「{self.command} 白肉雞 108/12」")
        self.product = params[1]
        self.query_date = params[2]

    def filter_products(self, products):
        products = products.replace('家畜類\n', '').replace('豬\n', '').replace('牛\n', '').replace('羊\n', '').replace('鹿\n', '')
        products = products.replace('家禽類\n', '').replace('火雞\n', '').replace('鴕鳥\n', '').replace('雞\n', '').replace('鴨\n', '').replace('鵝\n', '')
        products = products.replace('完全飼料\n', '').replace('飼料原料\n', '').replace('草料\n', '').replace('飼料\n', '')
        products = products.replace(' ', '\n').split('\n')
        return products


class Retail(LivestockPriceApiView):
    '''
    零售價api介面
    '''
    def __init__(self, params):
        super(Retail, self).__init__(params)
        self.check_type = "hldContent_rptPriceType_chkPriceType_2"

        if not len(params) == 3:
            raise CustomError(f"{self.command}的指令為「{self.command} 品項 年份」或「{self.command} 品項 年份/月份」，例如：\n「{self.command} 雞蛋 108」\n「{self.command} 雞蛋 108/12」")
        self.product = params[1]
        self.query_date = params[2]

    def filter_products(self, products):
        products = products.replace('家畜類\n', '').replace('豬\n', '').replace('牛\n', '').replace('羊\n', '')
        products = products.replace('家禽類\n', '').replace('雞\n', '').replace('鴨\n', '').replace('鵝\n', '')
        products = products.replace(' ', '\n').split('\n')
        return products
