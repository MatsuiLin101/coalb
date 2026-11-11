import json

from django.urls import reverse

from core.settings import (
    PROXY_DOMAIN,
    PROXY_TOKEN
)

from .configs import *


class CropPriceApiView(BasicApiView):
    """
    農耕價格api介面

    - CropPriceApiView(價格)
        必需先執行 builder CropPriceOriginBuilder 建立產地價的選項資料

    -- CropPriceOrigin(產地價)
        Builder: CropPriceOriginBuilder
        Proxy: True
        Data:
            農糧署農產品產地價格查報系統
            https://apis.afa.gov.tw/pagepub/AppContentPage.aspx?itemNo=PRI105

    -— CropPriceWholesale(批發價)
        Builder: None
        Proxy: False
        Data:
            農業統計資料查詢 qcode=CH04（蔬菜）、CH06（果品）、CH01（白米）
            https://agrstat.moa.gov.tw/moasdweb/inquire/InquireAdvance.aspx?qcode=CH04
    """
    def __init__(self, params):
        self.params = params
        self.command = params[0]

    def get_data(self):
        """繼承BasicApiView必須實作"""
        pass

    def choose_api(self):
        if self.command in ['產地', '產地價']:
            return CropPriceOriginApiView(self.params, use_proxy=True)
        elif self.command in ['批發', '批發價']:
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
            self.query_date = f'{self.year}年'
            self.select_date = str(self.year).zfill(3)
        except Exception as e:
            self.message = f'年份「{self.year}」無效，請輸入民國年'
            raise CustomError(self.message)
        if self.month:
            try:
                self.month = int(self.month)
                self.select_date += str(self.month).zfill(2)
                if not 1 <= self.month <= 12:
                    self.message = f'月份「{self.month}」請輸入1~12'
                    raise CustomError(self.message)
                self.query_date += f'{self.month}月'
            except Exception as e:
                self.message = f'月份「{self.month}」無效，請輸入1~12'
                raise CustomError(self.message)


class CropPriceOriginApiView(CropPriceApiView):
    """
    -- CropPriceOrigin(產地價)
        農糧署農產品產地價格查報系統
        https://apis.afa.gov.tw/pagepub/AppContentPage.aspx?itemNo=PRI105
    """
    def __init__(self, params, use_proxy=False):
        self.driver = None
        self.url = 'https://apis.afa.gov.tw/pagepub/AppContentPage.aspx?itemNo=PRI105'
        self.id_radio_month = 'WR1_1_Q_AvgPriceType_C1_1'
        self.id_select_year_start = 'WR1_1_Q_PRSR_Year1_C1'
        self.id_select_year_end = 'WR1_1_Q_PRSR_Year2_C1'
        self.id_select_month_start = 'WR1_1_Q_PRSR_Month1_C1'
        self.id_select_month_end = 'WR1_1_Q_PRSR_Month2_C1'
        self.id_category = 'WR1_1_Q_GroupCode_XX_C1'
        self.id_result_table = 'WR1_1_WG1'
        self.year = ''
        self.month = ''
        self.result = list()
        self.message = ''
        self.params = params
        self.use_proxy = use_proxy

        self.command = params[0]
        if len(params) == 3:
            self.city = None
            self.product = params[1]
            self.query_date = params[2]
        elif len(params) == 4:
            self.city = params[1].replace('臺', '台')
            self.product = params[2]
            self.query_date = params[3]
        else:
            raise CustomError('產地價的指令為「產地 品項 年份」也可加上縣市或月份「產地 縣市 品項 年份/月份」，例如：\n「產地 芒果 108」\n「產地 芒果 108/7」\n「產地 屏東 芒果 108」\n「產地 屏東 芒果 108/7」')

        self.command_text = ' '.join(text for text in params)

    def execute_api(self):
        if self.use_proxy:
            data = json.dumps({
                'params': self.params
            })
            res = requests.get(f"{PROXY_DOMAIN}{reverse('coa:proxy_parser')}?token={PROXY_TOKEN}&api=CropPriceOriginApiView&data={data}")
            if res.status_code != 200:
                return '該功能維護中...'
            return res.text
        else:
            return super(CropPriceOriginApiView, self).execute_api()

    def get_product(self):
        qs = CropPriceOrigin.objects.filter(name__icontains=self.product)
        if qs.count() == 0:
            self.message = f'查無品項「{self.product}」'
            raise CustomError(self.message)
        elif qs.count() > 5:
            self.message = f'搜尋品項「{self.product}」結果過多，請修改關鍵字後重新查詢：\n' + '\n'.join(obj.name for obj in qs)
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
            driver_select(self.driver, self.id_select_month_start, 'value', str(self.month))
            driver_select(self.driver, self.id_select_month_end, 'value', str(self.month))

        # select_year_start = self.driver.find_element(By.ID, self.id_select_year_start)
        # select_year_end = self.driver.find_element(By.ID, self.id_select_year_end)
        try:
            driver_select(self.driver, self.id_select_year_start, 'value', str(self.year + 1911))
            driver_select(self.driver, self.id_select_year_end, 'value', str(self.year + 1911))
        except Exception as e:
            select_year_start = self.driver.find_element(By.ID, self.id_select_year_start)
            options_year = select_year_start.find_elements(By.TAG_NAME, 'option')
            option_year_start = int(options_year[0].text) - 1911
            option_year_end = int(options_year[-1].text) - 1911
            self.message = f'年份「{self.year}」超過範圍，請輸入{option_year_start}～{option_year_end}'
            raise CustomError(self.message)

    def get_query(self, obj):
        select_category = self.driver.find_element(By.ID, self.id_category)
        obj_category = obj.category
        obj_id_table = obj.id_table
        obj_id_query = obj.id_query
        obj_id = obj.code
        obj_name = obj.name
        driver_select(self.driver, self.id_category, 'text', obj_category)
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
        self.driver.switch_to.window(window_new)
        WebDriverWait(self.driver, 30, 0.1).until(EC.presence_of_element_located((By.ID, self.id_result_table)))
        result_table = self.driver.find_element(By.ID, self.id_result_table)
        result = result_table.text
        self.driver.close()
        self.driver.switch_to.window(window_origin)
        return result

    def calc_result(self):
        self.list_result = list()
        for result in self.result:
            total = 0
            obj = result[0]
            data = result[1]
            rows = data.split('\n')[1:]
            if len(rows) == 0:
                self.list_result.append(f'{obj.name}：查無結果。')
            elif self.city:
                # 有指定縣市
                for row in rows:
                    if self.city in row:
                        cell = row.split(' ')
                        self.list_result.append((obj, f'{cell[0]} {cell[1]}：{round(float(cell[2]), 2)}(元/公斤)'))
            else:
                # 沒有指定縣市
                for row in rows:
                    total += float(row.split(' ')[-1])
                avg_total = round(total / len(rows), 2)
                self.list_result.append(f'{obj.name}：{avg_total}(元/公斤)')

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
            self.message = f'{self.year}年_month_ {self.city} {self.product} 產地價：\n'
            product = None
            for result in self.list_result:
                if type(result) == str:
                    self.message += f'{result}\n'
                    continue
                if product != result[0]:
                    product = result[0]
                    self.message += f'{product}\n'
                self.message += f'{result[1]}\n'
            self.message = self.message[:-1]
        else:
            self.message = f'{self.year}年_month_ {self.product} 產地價：\n' + '\n'.join(result for result in self.list_result)
        if self.month:
            self.message = self.message.replace('_month_', f'{self.month}月')
        else:
            self.message = self.message.replace('_month_', '')


class CropPriceWholesaleApiView(InquireAdvanceBasicApiView):
    """
    -— CropPriceWholesale(批發價)
        農業統計資料查詢 [農業生產統計]>>[農產品價格統計]>>[蔬菜批發價格-按批發蔬菜別]、[果品批發價格-按批發果品別]、[稻米產地及批發價格-按稻種別]
        https://agrstat.moa.gov.tw/moasdweb/inquire/InquireAdvance.aspx?qcode=CH04
        https://agrstat.moa.gov.tw/moasdweb/inquire/InquireAdvance.aspx?qcode=CH06
        https://agrstat.moa.gov.tw/moasdweb/inquire/InquireAdvance.aspx?qcode=CH01
        蔬菜和白米只有年資料，果品有年和月資料
    """
    # (qcode, 品項分類名稱, 統計量名稱)
    tables = [
        ('CH04', '批發蔬菜別', '蔬菜批發價格'),
        ('CH06', '批發果品別', '果品批發價格'),
        ('CH01', '稻種別', '白米批發(躉售)價格'),
    ]
    max_products = 5

    def __init__(self, params):
        self.driver = None
        self.year = ''
        self.month = None
        self.message = ''
        self.params = params

        if len(params) != 3:
            raise CustomError('批發的指令為「批發 品項 年份」，果品也可加上月份「批發 品項 年份/月份」，例如：\n「批發 甘藍 113」\n「批發 香蕉 114/6」')

        self.command = params[0]
        self.product = params[1]
        self.query_date = params[2]
        self.command_text = ' '.join(text for text in params)

    def verify_date(self):
        CropPriceApiView.verify_date(self)

    def query_table(self, group, item, products):
        """在已開啟的資料表查詢多個品項，回傳每個品項一行的結果"""
        try:
            self.inquire_period(self.year, self.month)
        except CustomError as e:
            reason = str(e).replace(f'「{self.command_text}」', '')
            return [f'{product}：{reason}' for product in products]
        self.inquire_dimension({group: products})
        self.inquire_items([item])
        self.inquire_period(self.year, self.month)
        self.inquire_submit()
        records = self.inquire_records()
        lines = list()
        for product in products:
            record = self.find_record(records, product)
            unit = re.search(r'\(([^()]*)\)\s*$', record['head'][0])
            if record['value'].strip() in ['', '-', '…', '...']:
                lines.append(f'{product}：查無結果')
            else:
                lines.append(f'{product}：{record["value"]}{f"({unit.group(1)})" if unit else ""}')
        return lines

    def get_data(self):
        found = list()
        for qcode, group, item in self.tables:
            self.qcode = qcode
            self.inquire_open()
            dimension = next(d for d in self.inquire_dimensions() if d['group'] == group)
            products = [c['name'] for c in self.match_names(dimension['codes'], self.product, multiple=True)]
            if products:
                found.append((qcode, group, item, products))

        count = sum(len(products) for *_, products in found)
        if count == 0:
            self.message = f'查無品項「{self.product}」'
            raise CustomError(self.message)
        if count > self.max_products:
            names = [name for *_, products in found for name in products]
            self.message = f'品項「{self.product}」有多個搜尋結果，請改用完整關鍵字如下：\n' + '\n'.join(names)
            raise CustomError(self.message)

        result = list()
        for qcode, group, item, products in found:
            self.qcode = qcode
            self.inquire_open()
            result += self.query_table(group, item, products)

        date = f'{self.year}年{self.month}月' if self.month else f'{self.year}年'
        self.message = f'{date} {self.product} 批發：\n' + '\n'.join(result)
