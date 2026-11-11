from .configs import *


class LaborforceApiView(InquireAdvanceBasicApiView):
    """
    勞動力(就業人口)api介面
    laborforce(勞動力)

    - Laborforce(勞動力)
        Builder: None
        Proxy: False
        Data:
            農業統計資料查詢 [農民(農戶)統計]>>[勞動力統計]>>[農業就業人口-按行業別]
            https://agrstat.moa.gov.tw/moasdweb/inquire/InquireAdvance.aspx?qcode=BA05
            改版後只有年資料，沒有月資料
    """
    qcode = 'BA05'

    def __init__(self, params):
        self.driver = None
        self.message = ''
        self.year = ''
        self.month = ''

        if not len(params) == 2:
            raise CustomError('就業人口的指令為「就業人口 年份」，例如：\n「就業人口 113」')
        self.command = params[0]
        self.query_date = params[1]
        self.command_text = ' '.join(text for text in params)

    def verify_date(self):
        # 檢查年份是否為數字
        if '/' in self.query_date:
            self.year, self.month = self.query_date.split('/', 1)
        else:
            self.year = self.query_date
        try:
            self.year = int(self.year)
        except Exception as e:
            self.message = f'年份「{self.year}」無效，請輸入民國年'
            raise CustomError(self.message)
        # 檢查月份是否為數字
        if self.month:
            try:
                self.month = int(self.month)
            except Exception as e:
                self.message = f'月份「{self.month}」無效，請輸入1～12'
                raise CustomError(self.message)

    def get_data(self):
        self.inquire_open()
        self.inquire_items()
        self.inquire_period(self.year, self.month)
        self.inquire_submit()
        record = self.inquire_records()[0]
        # 表頭為「農業就業人口(千人)」
        unit = record['head'][0].split('人口')[-1]
        self.message = f'{self.year}年 就業人口：{record["value"]}{unit}'
