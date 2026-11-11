from .configs import *


class CropCostApiView(InquireAdvanceBasicApiView):
    """
    農耕生產成本api介面

    - CropCost(生產成本)
        Builder: None
        Proxy: False

    -- TotalCost(生產成本)
        同時查詢生產成本、粗收益、淨收入率、工時

    -- ProduceCost(生產成本)
        Data:
            農業統計資料查詢 [農業經營統計]>>[生產成本統計]>>[平均每公頃農產品生產成本]>>[每公頃生產成本：生產成本總計]
            https://agrstat.moa.gov.tw/moasdweb/inquire/InquireAdvance.aspx?qcode=DA02

    -- CrudeIncome(粗收益)
        Data:
            農業統計資料查詢 [農業經營統計]>>[生產成本統計]>>[平均每公頃農產品生產成本]>>[每公頃生產量與收益：粗收益]
            https://agrstat.moa.gov.tw/moasdweb/inquire/InquireAdvance.aspx?qcode=DA02

    -- PureIncomeRate(淨收入率)
        淨收入率 = (粗收益 - 生產成本) / 粗收益

    -- WorkHour(工時)
        Data:
            農業統計資料查詢 [農業經營統計]>>[生產成本統計]>>[農產品每公頃人工時數-按農產品項目]>>[男工＋女工]合計
            https://agrstat.moa.gov.tw/moasdweb/inquire/InquireAdvance.aspx?qcode=DA03
    """
    qcode_cost = 'DA02'
    qcode_hour = 'DA03'
    group_product = '生產成本與收益_農產品項目'
    unit_cost = '(元/公頃)'
    unit_rate = '(%)'
    unit_hour = '(小時/公頃)'

    def __init__(self, params):
        self.driver = None
        self.message = ''
        self.params = params
        self.product_name = None

        if len(params) != 3:
            raise CustomError('生產成本(生產成本、粗收益、淨收入率、工時)的指令為「成本 作物 年份」，例如：\n「成本 香蕉 113」\n\n也可單獨查詢，例如：\n「生產費用 香蕉 113」\n「粗收益 香蕉 113」\n「淨收入率 香蕉 113」\n「工時 香蕉 113」')
        self.command = params[0]
        self.product = params[1]
        self.query_date = params[2]
        self.command_text = ' '.join(text for text in params)

    def choose_api(self):
        if self.command in ['成本', '生產成本']:
            return TotalCost(self.params)
        elif self.command in ['費用', '生產費用']:
            return ProduceCost(self.params)
        elif self.command in ['粗收益']:
            return CrudeIncome(self.params)
        elif self.command in ['收入', '淨收入', '淨收入率']:
            return PureIncomeRate(self.params)
        elif self.command in ['工時']:
            return WorkHour(self.params)

    def get_data(self):
        """繼承BasicApiView必須實作，由子類別實作"""
        pass

    def get_product(self):
        """在已開啟的頁面找出品項名稱；有多個相似品項時請使用者改用完整名稱"""
        if self.product_name:
            return self.product_name
        dimension = next(d for d in self.inquire_dimensions() if d['group'] == self.group_product)
        matched = self.match_names(dimension['codes'], self.product, multiple=True)
        exact = [c for c in matched if c['name'] == self.product.replace('台', '臺')]
        if exact or len(matched) == 1:
            self.product_name = (exact or matched)[0]['name']
            return self.product_name
        if matched:
            self.message = f'品項「{self.product}」有多個搜尋結果，請改用完整關鍵字如下：\n' + '\n'.join(c['name'] for c in matched)
        else:
            self.message = f'查無品項「{self.product}」'
        raise CustomError(self.message)

    def query_cost(self, cost=True, income=True):
        """查詢每公頃生產成本總計、粗收益，回傳 (生產成本, 粗收益) 的文字"""
        self.qcode = self.qcode_cost
        self.inquire_open()
        selections = {self.group_product: [self.get_product()]}
        items = list()
        if cost:
            selections['每公頃生產成本'] = ['生產成本總計']
            items.append('農產品每公頃生產成本')
        if income:
            selections['每公頃生產量與收益'] = ['粗收益(元)']
            items.append('農產品每公頃生產量與收益')
        self.inquire_dimension(selections)
        self.inquire_items(items)
        self.inquire_period(self.year)
        self.inquire_submit()
        records = self.inquire_records()
        result_cost = self.find_record(records, '生產成本總計')['value'] if cost else None
        result_income = self.find_record(records, '粗收益')['value'] if income else None
        return result_cost, result_income

    def query_hour(self):
        """查詢每公頃人工時數（男工＋女工），回傳文字"""
        self.qcode = self.qcode_hour
        self.inquire_open()
        self.inquire_dimension({self.group_product: [self.get_product()], '人工時數': None})
        self.inquire_items()
        self.inquire_period(self.year)
        self.inquire_submit()
        records = self.inquire_records()
        male = self.find_record(records, '男工')['value']
        female = self.find_record(records, '女工')['value']
        if is_empty(male) and is_empty(female):
            return '查無資料'
        try:
            return f'{round(to_number(male) + to_number(female)):,d}{self.unit_hour}'
        except Exception as e:
            return f'無法計算，男工：{male}、女工：{female}'

    def income_rate(self, cost, income):
        if is_empty(cost) or is_empty(income):
            return '查無資料'
        try:
            cost, income = to_number(cost), to_number(income)
            return f'{round((income - cost) / income * 100):,d}{self.unit_rate}'
        except Exception as e:
            return f'無法計算，生產成本：{cost}、粗收益：{income}'

    def with_unit(self, value, unit):
        if is_empty(value):
            return '查無資料'
        try:
            return f'{round(to_number(value)):,d}{unit}'
        except Exception as e:
            return value


def to_number(text):
    return float(text.replace(',', ''))


def is_empty(text):
    """網站用「…」或「-」表示該年度沒有資料"""
    return text.strip() in ['', '-', '…', '...']


class TotalCost(CropCostApiView):
    """
    -- TotalCost(生產成本)
        同時查詢生產成本、粗收益、淨收入率、工時
    """
    def get_data(self):
        cost, income = self.query_cost()
        hour = self.query_hour()
        self.message = f'{self.year}年 {self.product_name} {self.command}：\n'
        self.message += f'生產成本：{self.with_unit(cost, self.unit_cost)}\n'
        self.message += f'粗收益：{self.with_unit(income, self.unit_cost)}\n'
        self.message += f'淨收入率：{self.income_rate(cost, income)}\n'
        self.message += f'工時：{hour}'


class ProduceCost(CropCostApiView):
    """
    -- ProduceCost(生產成本)
    """
    def get_data(self):
        cost, _ = self.query_cost(income=False)
        self.message = f'{self.year}年 {self.product_name} {self.command}：{self.with_unit(cost, self.unit_cost)}'


class CrudeIncome(CropCostApiView):
    """
    -- CrudeIncome(粗收益)
    """
    def get_data(self):
        _, income = self.query_cost(cost=False)
        self.message = f'{self.year}年 {self.product_name} {self.command}：{self.with_unit(income, self.unit_cost)}'


class PureIncomeRate(CropCostApiView):
    """
    -- PureIncomeRate(淨收入率)
        淨收入率 = (粗收益 - 生產成本) / 粗收益
    """
    def get_data(self):
        cost, income = self.query_cost()
        self.message = f'{self.year}年 {self.product_name} {self.command}：{self.income_rate(cost, income)}'


class WorkHour(CropCostApiView):
    """
    -- WorkHour(工時)
    """
    def get_data(self):
        hour = self.query_hour()
        self.message = f'{self.year}年 {self.product_name} {self.command}：{hour}'
