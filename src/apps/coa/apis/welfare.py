from .configs import *


class WelfareApiView(InquireAdvanceBasicApiView):
    """
    社會福利api介面
    welfare(社會福利)

    - Insurance(農保)
        Builder: None
        Proxy: False
        Data:
            農業統計資料查詢 [農民(農戶)統計]>>[社會保險統計]>>[農民健康保險投保單位、人數及應計保險費-按縣市別]
            https://agrstat.moa.gov.tw/moasdweb/inquire/InquireAdvance.aspx?qcode=BB01

    - Allowance(老農津貼)
        Builder: None
        Proxy: False
        Data:
            農業統計資料查詢 [農民(農戶)統計]>>[社會福利統計]>>[老年農民福利津貼核付人數及金額-按縣市別]
            https://agrstat.moa.gov.tw/moasdweb/inquire/InquireAdvance.aspx?qcode=BC01

    - Scholarship(農漁民子女獎助學金)
        Builder: None
        Proxy: False
        Data:
            農業統計資料查詢 [農民(農戶)統計]>>[社會福利統計]>>[獎勵農漁民子女就學金發放件數、金額及受益學生人次-按縣市別]
            https://agrstat.moa.gov.tw/moasdweb/inquire/InquireAdvance.aspx?qcode=BC02
            只有年資料
    """
    command_name = ''
    usage = ''

    def __init__(self, params):
        self.driver = None
        self.year = ''
        self.month = ''
        self.message = ''
        self.params = params
        self.command = params[0]

        if self.usage and not 2 <= len(params) <= 3:
            raise CustomError(self.usage)
        if len(params) == 3:
            self.city = params[1].replace('台', '臺')
            self.query_date = params[2]
        elif len(params) == 2:
            self.city = None
            self.query_date = params[1]
        self.command_text = ' '.join(text for text in params)

    def get_data(self):
        """繼承BasicApiView必須實作"""
        pass

    def choose_api(self):
        if self.command in ['農保']:
            return Insurance(self.params)
        elif self.command in ['津貼', '老農津貼']:
            return Allowance(self.params)
        elif self.command in ['獎學金', '助學金', '獎助學金']:
            return Scholarship(self.params)

    def verify_date(self):
        # 檢查年份是否為數字
        if '/' in self.query_date:
            self.year, self.month = self.query_date.split('/', 1)
        else:
            self.year = self.query_date
        try:
            self.year = int(self.year)
        except Exception as e:
            self.message = f"年份「{self.year}」無效，請輸入民國年"
            raise CustomError(self.message)
        # 檢查月份是否為數字
        if self.month:
            try:
                self.month = int(self.month)
            except Exception as e:
                self.message = f"月份「{self.month}」無效，請輸入1～12"
                raise CustomError(self.message)

    def query(self, items):
        """
        查詢統計量 items（可多個），回傳 (縣市名稱, [各統計量的「值(單位)」])
        沒有指定縣市時查全國合計，單位取自表頭，例如「老農津貼金額(元)」
        """
        self.inquire_open()
        city = None
        if self.city:
            city = self.inquire_dimension({'縣市別': [self.city]})['縣市別'][0]
        self.inquire_items(items)
        self.inquire_period(self.year, self.month)
        self.inquire_submit()
        records = self.inquire_records()
        results = list()
        for item in items:
            record = self.find_record(records, item)
            unit = re.search(r'\(([^()]*)\)\s*$', record['head'][0])
            results.append(f"{record['value']}({unit.group(1)})" if unit else record['value'])
        return city, results

    def title(self, city):
        text = f"{self.year}年"
        if self.month:
            text += f"{self.month}月"
        if city:
            text += f" {city}"
        return text


class Insurance(WelfareApiView):
    """
    農保api介面

    - Insurance(農保)
        https://agrstat.moa.gov.tw/moasdweb/inquire/InquireAdvance.aspx?qcode=BB01
    """
    qcode = 'BB01'
    usage = '農保的指令為「農保 年份」或「農保 年份/月份」，例如：\n「農保 113」\n「農保 114/6」\n\n也可加上縣市「農保 縣市 年份」或「農保 縣市 年份/月份」，例如：\n「農保 高雄 113」\n「農保 高雄 114/6」'

    def get_data(self):
        city, (result, ) = self.query(['農民健康保險投保人數'])
        self.message = f"{self.title(city)} 農保：{result}"


class Allowance(WelfareApiView):
    """
    老農津貼api介面

    - Allowance(老農津貼)
        https://agrstat.moa.gov.tw/moasdweb/inquire/InquireAdvance.aspx?qcode=BC01
    """
    qcode = 'BC01'
    usage = '老農津貼的指令為「老農津貼 年份」或「老農津貼 年份/月份」，例如：\n「老農津貼 113」\n「老農津貼 114/6」\n\n也可加上縣市「老農津貼 縣市 年份」或「老農津貼 縣市 年份/月份」，例如：\n「老農津貼 高雄 113」\n「老農津貼 高雄 114/6」'

    def get_data(self):
        city, (result1, result2) = self.query(['老農津貼人數', '老農津貼金額'])
        self.message = f"{self.title(city)} 老農津貼人數：{result1}\n"
        self.message += f"{self.title(city)} 老農津貼金額：{result2}"


class Scholarship(WelfareApiView):
    """
    農漁民子女獎助學金api介面

    - Scholarship(農漁民子女獎助學金)
        https://agrstat.moa.gov.tw/moasdweb/inquire/InquireAdvance.aspx?qcode=BC02
    """
    qcode = 'BC02'
    usage = '獎助學金的指令為「獎助學金 年份」，例如：\n「獎助學金 113」\n\n也可加上縣市「獎助學金 縣市 年份」，例如：\n「獎助學金 高雄 113」'

    def get_data(self):
        city, (result1, result2) = self.query(['農漁民子弟就學獎助學金發放件數', '農漁民子弟就學獎助學金發放金額'])
        self.message = f"{self.title(city)} 農漁民子女獎助學金發放件數：{result1}\n"
        self.message += f"{self.title(city)} 農漁民子女獎助學金金額：{result2}"
