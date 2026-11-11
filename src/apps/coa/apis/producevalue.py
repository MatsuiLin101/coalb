from .configs import *


class ProduceValueApiView(BasicApiView):
    """
    產值api介面

    - ProduceValue(產值)

    -- TotalValue(總產值)
        Builder: None
        Proxy: False
        Data:
            農業統計資料查詢 [農業生產統計]>>[農業產值結構與指標]>>[農業產值-按縣市別]
            https://agrstat.moa.gov.tw/moasdweb/inquire/InquireAdvance.aspx?qcode=CA02

    -- Value(產值)
        Builder: None
        Proxy: False
        Data:
            年報
            一、農業經濟指標
            (四)農產品生產量值
            https://agrstat.moa.gov.tw/sdweb/public/book/Book.aspx
    """
    def __init__(self, params):
        self.params = params
        self.command = params[0]

    def get_data(self):
        """繼承BasicApiView必須實作"""
        pass

    def choose_api(self):
        if self.command in ['總產值']:
            return TotalValueApiView(self.params)
        elif self.command in ['產值']:
            return ValueApiView(self.params)
        else:
            raise CustomError('查詢介面指令錯誤，請通知管理員處理。')


class TotalValueApiView(InquireAdvanceBasicApiView):
    """
    -- TotalValue(總產值)
        農業統計資料查詢 [農業生產統計]>>[農業產值結構與指標]>>[農業產值-按縣市別]
        https://agrstat.moa.gov.tw/moasdweb/inquire/InquireAdvance.aspx?qcode=CA02
    """
    qcode = 'CA02'
    categories = ['農產', '林產', '畜產', '漁產']

    def __init__(self, params):
        self.driver = None
        self.message = ''
        self.params = params

        self.command = params[0]
        if len(params) == 2:
            self.city = None
            self.query_date = params[1]
        elif len(params) == 3:
            self.city = params[1].replace('台', '臺')
            self.query_date = params[2]
        else:
            raise CustomError('總產值的指令為「總產值 年份」或可加上城市「總產值 城市 年份」，例如：\n「總產值 107」\n「總產值 台中 108」')

        self.command_text = ' '.join(text for text in params)

    def get_data(self):
        self.inquire_open()
        selections = {'農業別': None}
        if self.city is not None:
            selections['縣市別'] = [self.city]
        picked = self.inquire_dimension(selections)
        self.inquire_items()
        self.inquire_period(self.year)
        self.inquire_submit()
        records = self.inquire_records()

        # 第一欄是合計（農業），其餘依農業別
        results = [records[0]['value']] + [self.find_record(records, category)['value'] for category in self.categories]
        title = f'{self.year}年 {picked["縣市別"][0]} 總產值：\n' if self.city is not None else f'{self.year}年 總產值：\n'
        self.message = title + '\n'.join(
            f'{name}：{value}(千元)' for name, value in zip(['農業'] + self.categories, results)
        )


class ValueApiView(AnnualReportBasicApiView):
    """
    -- Value(產值)
        年報
        一、農業經濟指標
        (四)農產品生產量值
        https://agrstat.moa.gov.tw/sdweb/public/book/Book.aspx
    """
    def __init__(self, params):
        super(ValueApiView, self).__init__(params)
        self.id_ods = 'ctl00_cphMain_uctlBook_repChapter_ctl06_dtlFile_ctl00_lnkFile'

        if len(params) != 3:
            raise CustomError('產值的指令為「產值 品項 年份」，例如：\n「產值 稻米 110」')

        self.command = params[0]
        self.product = params[1]
        self.query_date = params[2]

    def open_wb(self):
        """
        讀取年報檔案
        """
        wb = load_workbook(filename=self.xlsx_name)
        self.list_ws = [wb[sheetname] for sheetname in wb.sheetnames]

    def verify_year_exist(self):
        """
        檢查查詢年份是否在年報中
        """
        ws = self.list_ws[0]
        list_years = [ws['G5'], ws['K5'], ws['P5'], ws['T5']]  # 年報中的4個年份欄位

        if not any(str(self.year) in year.value for year in list_years):
            self.message = f'「{self.command_text}」年份必須符合以下：\n' + '\n'.join(year.value for year in list_years)
            raise CustomError(self.message)
        else:
            match_year = [year for year in list_years if str(self.year) in year.value][0]
            col_year = match_year.col_idx  # 取得對應年份的欄位索引 A = 0, B = 1
            self.col_value = col_year - 1 + 2  # 對應欄位索引 -1 + 2 為該年份的產值欄位索引

    def get_data(self):
        """
        從年報中查詢資料
        """
        list_result = list()
        for ws in self.list_ws:
            for row in ws.rows:
                # 跳過前13row
                if row[0].row <= 13:
                    continue

                # 每個row的D欄位是產品名稱 比對產品名稱是否為查詢品項
                if row[3].value is not None and self.product in row[3].value:
                    value = row[self.col_value].value
                    list_result.append((row[3].value, value))

        if list_result:
            self.message = '\n'.join(f'{self.year}年 {result[0]} 產值：{round(result[1]):,d}(千元)' for result in list_result)
            self.message += f'\n\n資料來源：{self.source}'
        else:
            self.message = f'{self.year}年 {self.product} 產值：查無資料'
