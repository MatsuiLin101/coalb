import json

from django.urls import reverse

from core.settings import (
    PROXY_DOMAIN,
    PROXY_TOKEN
)

from .configs import *


class LivestockHogApiView(BasicApiView):
    """
    毛豬價格api介面

    - amount(交易量)
    - price(價格)
    - weight(重量)
        Builder: None
        Proxy: True（網站擋海外 IP，主站經代理站查詢）
        Data:
            畜產行情資訊網 https://ppg.naif.org.tw/naif/MarketInformation/Pig/twStatistics.aspx
    """
    def __init__(self, params, use_proxy=False):
        self.driver = None
        self.use_proxy = use_proxy
        self.url = 'https://ppg.naif.org.tw/naif/MarketInformation/Pig/twStatistics.aspx'
        self.check_month = 'ContentPlaceHolder_main_RadioButton_m'
        self.select_month_start_year = 'ContentPlaceHolder_main_DropDownList_m_begYear'
        self.select_month_start_month = 'ContentPlaceHolder_main_DropDownList_m_begMonth'
        self.select_month_end_year = 'ContentPlaceHolder_main_DropDownList_m_endYear'
        self.select_month_end_month = 'ContentPlaceHolder_main_DropDownList_m_endMonth'
        self.check_year = 'ContentPlaceHolder_main_RadioButton_y'
        self.select_year_start_year = 'ContentPlaceHolder_main_DropDownList_y_beg'
        self.select_year_end_year = 'ContentPlaceHolder_main_DropDownList_y_end'
        self.check_penghu = 'ContentPlaceHolder_main_CheckBox_penghu'
        self.btn_query = 'ContentPlaceHolder_main_Button_query'
        self.table = 'ContentPlaceHolder_main_GridView_data'
        # 結果表格的欄位標題（兩層標題以「/」串接），依需求確認表，頭數、重量、價格都取規格豬
        self.col_date = '日期'
        self.col_amount = '規格豬/成交頭數'
        self.col_weight = '規格豬/平均重量'
        self.col_price = '規格豬/平均價格'
        self.message = ''
        self.params = params

        self.command = params[0]
        if len(params) == 2:
            self.query_date = params[1]
        elif len(params) == 3:
            self.product = params[1]
            self.query_date = params[2]
        else:
            raise CustomError('毛豬(不包含澎湖)的指令為「毛豬 年份」或「毛豬 年份/月份」，例如：\n「毛豬 108」\n「毛豬 108/12」\n\n也使用替代指令查詢(皆可帶入月份)，例如：\n「交易量 豬 107」\n「價格 豬 108/12」\n「重量 豬 109/1」')

        self.command_text = ' '.join(text for text in params)

    def choose_api(self):
        """由 LINE 指令進來時一律經代理站查詢；代理站的 Celery 直接建立物件，不會經過這裡"""
        return LivestockHogApiView(self.params, use_proxy=True)

    def execute_api(self):
        if self.use_proxy:
            data = json.dumps({
                'params': self.params
            })
            res = requests.get(f"{PROXY_DOMAIN}{reverse('coa:proxy_parser')}?token={PROXY_TOKEN}&api=LivestockHogApiView&data={data}")
            if res.status_code != 200:
                return '該功能維護中...'
            return res.text
        else:
            return super(LivestockHogApiView, self).execute_api()

    def verify_date(self):
        try:
            if '/' in self.query_date:
                self.year, self.month = self.query_date.split('/')
            else:
                self.year = self.query_date
                self.month = None
        except Exception as e:
            self.message = f'日期「{self.query_date}」發生錯誤，請輸入民國年、民國年/月份\n例如：\n108\n109/12'
            raise CustomError(self.message)
        # 檢查年份是否為數字
        try:
            self.year = int(self.year)
            self.year += 1911
        except Exception as e:
            self.message = f'年份「{self.year}」無效，請輸入民國年'
            raise CustomError(self.message)
        # 檢查月份是否為數字
        if self.month:
            try:
                self.month = int(self.month)
                if not 1 <= self.month <= 12:
                    self.message = f'月份「{self.month}」無效，請輸入1～12'
                    raise CustomError(self.message)
            except Exception as e:
                self.message = f'月份「{self.month}」無效，請輸入1～12'
                raise CustomError(self.message)

    def get_table(self):
        if self.month:
            btn_check_month = self.driver.find_element(By.ID, self.check_month)
            btn_check_month.send_keys('enter')
            btn_check_month.click()
            select_year = self.driver.find_element(By.ID, self.select_month_start_year)
            if not str(self.year) in select_year.text:
                range_year = select_year.text.replace(' ', '').split('\n')
                self.message = f'年份「{self.year - 1911}」必需在「{int(range_year[0]) - 1911}」到「{int(range_year[-1]) - 1911}」之間'
                raise CustomError(self.message)
            driver_select(self.driver, self.select_month_start_year, 'value', str(self.year))
            driver_select(self.driver, self.select_month_start_month, 'value', str(self.month))
            driver_select(self.driver, self.select_month_end_year, 'value', str(self.year))
            driver_select(self.driver, self.select_month_end_month, 'value', str(self.month))
            time.sleep(1)
        else:
            btn_check_year = self.driver.find_element(By.ID, self.check_year)
            btn_check_year.send_keys('enter')
            time.sleep(1)
            btn_check_year.click()
            select_year = self.driver.find_element(By.ID, self.select_year_start_year)
            if not str(self.year) in select_year.text:
                range_year = select_year.text.replace(' ', '').split('\n')
                self.message = f'年份「{self.year - 1911}」必需在「{int(range_year[0]) - 1911}」到「{int(range_year[-1]) - 1911}」之間'
                raise CustomError(self.message)
            driver_select(self.driver, self.select_year_start_year, 'value', str(self.year))
            driver_select(self.driver, self.select_year_end_year, 'value', str(self.year))
            time.sleep(1)

        btn_check_penghu = self.driver.find_element(By.ID, self.check_penghu)
        btn_check_penghu.send_keys('enter')
        time.sleep(1)
        btn_check_penghu.click()
        time.sleep(1)
        btn_query = self.driver.find_element(By.ID, self.btn_query)
        btn_query.click()

    def get_data(self):
        self.parser()
        self.get_table()
        table = self.driver.find_element(By.ID, self.table)
        if '查無資料' in table.text:
            if self.month:
                self.message = f'{self.year - 1911}年{self.month}月 豬 查無資料'
            else:
                self.message = f'{self.year - 1911}年 豬 查無資料'
            return
        rows = parse_table_by_header(table.get_attribute('outerHTML'))

        # 網站改了欄位標題時直接報錯，不要回傳錯的欄位
        columns = [self.col_date, self.col_amount, self.col_weight, self.col_price]
        missing = [col for col in columns if not rows or col not in rows[0]]
        if missing:
            raise Exception(f'毛豬結果表格找不到欄位 {missing}，網站可能改版，目前的欄位：{list(rows[0]) if rows else []}')

        # 核對日期欄，避免讀到別的年份或月份
        query_date = f'{self.year}-{self.month:02d}' if self.month else str(self.year)
        row = next((row for row in rows if row[self.col_date] == query_date), None)
        if row is None:
            raise Exception(f'毛豬結果表格找不到日期「{query_date}」的資料，表格中的日期：{[row[self.col_date] for row in rows]}')

        amount = row[self.col_amount]
        weight = row[self.col_weight]
        price = row[self.col_price]
        if self.month:
            title = f'{self.year - 1911}年{self.month}月 豬(不含澎湖)'
        else:
            title = f'{self.year - 1911}年 豬(不含澎湖)'
        self.message = f'{title}\n成交頭數(規格豬)：{amount}(頭)\n平均重量(規格豬)：{weight}(公斤)\n平均價格(規格豬)：{price}(元/公斤)'
