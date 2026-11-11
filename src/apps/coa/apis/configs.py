from abc import (
    ABC,
    abstractmethod
)

import pandas as pd

from apps.coa.utils import *


class BasicApiView(ABC):
    """
    Basic view for moa apis
    """
    def __init__(self, params):
        self.params = params
        self.command_text = ' '.join(text for text in params)

    @property
    def classname(self):
        return self.__class__.__name__

    @abstractmethod
    def get_data(self):
        """子類別必須實作這個方法"""
        pass

    def execute_api(self):
        """
        execute api
        """
        try:
            self.verify_date()
            self.get_data()
            return self.message
        except CustomError as ce:
            raise ce
        except Exception:
            traceback_log = TracebackLog.objects.create(app=f"{self.classname}", message=traceback.format_exc())
            self.message = f"搜尋「{self.command_text}」發生未知錯誤，錯誤編號「{traceback_log.id}」，請通知管理員處理。"
            raise CustomError(self.message)
        finally:
            if hasattr(self, 'driver') and self.driver:
                self.driver.quit()

    def parser(self):
        self.driver = get_driver()
        self.driver.get(self.url)

    def verify_date(self):
        """檢查年份是否為數字"""
        try:
            self.year = int(self.query_date)
        except Exception as e:
            self.message = f"年份「{self.query_date}」無效，請輸入民國年"
            raise CustomError(self.message)

    def get_table(self):
        # select_start_year = self.driver.find_element(By.ID, self.id_start_year)
        # select_end_year = self.driver.find_element(By.ID, self.id_end_year)
        value = str(self.year).zfill(3)
        try:
            driver_select(self.driver, self.id_start_year, 'value', value)
            driver_select(self.driver, self.id_end_year, 'value', value)
        except Exception as e:
            options = self.driver.find_element(By.ID, self.id_start_year).text.replace(' ', '').replace('年', '')
            options = options.split('\n')
            date_start = options[0]
            date_end = options[-1]
            self.message = f"年份「{self.query_date}」超出範圍，年份需介於「{date_start}」～「{date_end}」之間"
            raise CustomError(self.message)

        btn_query = self.driver.find_element(By.ID, self.id_query)
        btn_query.click()


class AnnualReportBasicApiView(BasicApiView):
    """
    年報用公版ApiView
    如果年報持續報錯，或是轉檔失敗，且時間在6~8月左右，可能是年報更新導致抓不到更新的年報
    """
    def __init__(self, params):
        self.driver = None
        self.url = 'https://agrstat.moa.gov.tw/sdweb/public/book/Book.aspx'
        self.radio_history = 'ctl00_cphMain_uctlBook_rdoPeriodAll'
        self.btn_total = 'ctl00_cphMain_uctlBook_chkQCategoryAll'
        self.btn_book = 'ctl00_cphMain_uctlBook_dltQCategory_ctl00_chkQCategory'
        self.btn_search = 'ctl00_cphMain_uctlBook_btnQuery'
        self.id_table = 'ctl00_cphMain_uctlBook_grdBook'
        self.id_book1 = ''
        self.id_book2 = ''
        self.xlsx_name = ''
        self.message = ''
        self.row = ''
        self.params = params
        self.command_text = ' '.join(text for text in params)

    def execute_api(self):
        try:
            self.verify_date()
            self.download()
            self.open_wb()
            self.verify_year_exist()
            self.get_data()
            return self.message
        except CustomError as ce:
            raise ce
        except Exception:
            traceback_log = TracebackLog.objects.create(app=f"{self.classname}", message=traceback.format_exc())
            self.message = f"「{self.command_text}」發生未知錯誤，錯誤編號「{traceback_log.id}」，請通知管理員處理"
            raise CustomError(self.message)
        finally:
            if hasattr(self, 'driver') and self.driver:
                self.driver.quit()

            if self.xlsx_name:
                os.remove(self.xlsx_name)

    def download(self):
        """
        避免年報更新時的空窗期，抓取最新一期的年報及前一期的年報，並備註資料來源
        """
        # download ods and transfer to xlsx
        self.driver = get_driver()
        try:
            self.driver.get(self.url)
            WebDriverWait(self.driver, 30, 0.1).until(EC.presence_of_element_located((By.ID, self.btn_search)))
            self.driver.find_element(By.ID, self.radio_history).click()
            self.driver.find_element(By.ID, self.btn_total).click()
            self.driver.find_element(By.ID, self.btn_book).click()
            self.driver.find_element(By.ID, self.btn_search).click()
            WebDriverWait(self.driver, 30, 0.1).until(EC.presence_of_element_located((By.ID, self.id_table)))
            table = self.driver.find_element(By.ID, self.id_table)
            reports = table.find_elements(By.TAG_NAME, 'a')
            for report in reports:
                if '農業統計年報' in report.text and self.id_book1 == '':
                    self.id_book1 = report.get_attribute('id')
                    self.source1 = report.text
                    continue
                elif '農業統計年報' in report.text and self.id_book2 == '':
                    self.id_book2 = report.get_attribute('id')
                    self.source2 = report.text
                    continue
                elif self.id_book1 and self.id_book2:
                    break

            try:
                self.driver.find_element(By.ID, self.id_book1).click()
                ods = self.driver.find_element(By.ID, self.id_ods)
                self.source = self.source1
            except Exception as e:
                try:
                    self.driver.get(self.url)
                    WebDriverWait(self.driver, 30, 0.1).until(EC.presence_of_element_located((By.ID, self.btn_search)))
                    self.driver.find_element(By.ID, self.radio_history).click()
                    self.driver.find_element(By.ID, self.btn_total).click()
                    self.driver.find_element(By.ID, self.btn_book).click()
                    self.driver.find_element(By.ID, self.btn_search).click()
                    WebDriverWait(self.driver, 30, 0.1).until(EC.presence_of_element_located((By.ID, self.id_book2)))
                    self.driver.find_element(By.ID, self.id_book2).click()
                    ods = self.driver.find_element(By.ID, self.id_ods)
                    self.source = self.source2
                except Exception as e:
                    raise

            # 產生 ods 及 xlsx 臨時檔名
            ods_href = ods.get_attribute('href')
            ods_name = f'ods_{int(datetime.datetime.now().timestamp())}.ods'
            xlsx_name = ods_name.replace('.ods', '.xlsx')

            # 抓取 ods 之後保存
            res = requests.get(ods_href)
            with open(ods_name, 'wb') as f:
                f.write(res.content)

            # pandas 搭配 odf 將 ods 轉檔成 xlsx
            df = pd.read_excel(ods_name, engine="odf")
            df.to_excel(xlsx_name, index=False, engine="openpyxl")

            self.xlsx_name = xlsx_name
            os.remove(ods_name)
        except Exception as e:
            raise

    def open_wb(self):
        """
        讀取年報檔案
        """
        wb = load_workbook(filename=self.xlsx_name)
        self.ws = wb[wb.sheetnames[0]]

    def verify_year_exist(self):
        """
        檢查查詢年份是否在年報中
        """
        list_years = list()
        for row in self.ws.rows:
            year = row[1].value
            if year is not None:
                try:
                    int(year)
                    list_years.append(year)
                except Exception as e:
                    continue

                if str(self.year) == str(year):
                    self.row = row[0].row
                    return
        self.message = f"「{self.command_text}」年份必需在{list_years[0]}~{list_years[-1]}之間"
        raise CustomError(self.message)


# 農業統計資料查詢（2026 年改版後的 agrstat.moa.gov.tw/moasdweb）共用的 JavaScript。
# 網站的勾選清單是用加密過的 JSON（hidCode 隱藏欄位）在瀏覽器端畫出來的，
# 直接改 JSON 裡的 Selected 再按「確定」，比一個一個點選單穩定。
JS_INQUIRE_CODE_HELPERS = """
var KEY = '2025000000000000';
function readCode(id) {
    var el = document.getElementById(id);
    return el ? JSON.parse(DecryptCode(KEY, el.value)) : null;
}
function writeCode(id, obj) {
    document.getElementById(id).value = EncryptCode(KEY, JSON.stringify(obj));
}
function codeName(label) {
    // label 內可能有「全選」的 span，只取第一個文字節點
    return (label.childNodes[0] ? label.childNodes[0].textContent : label.innerText).trim();
}
"""

JS_INQUIRE_DIMENSIONS = JS_INQUIRE_CODE_HELPERS + """
var prefix = arguments[0];
var result = [];
document.querySelectorAll('[id^="' + prefix + 'repTabs_ctl"][id$="_lnkTab"]').forEach(function (tab) {
    var ctl = tab.id.replace(prefix + 'repTabs_', '').replace('_lnkTab', '');
    var hids = document.querySelectorAll('[id^="' + prefix + 'repContents_' + ctl + '_"][id$="_hidCode"]');
    hids.forEach(function (hid) {
        var obj = readCode(hid.id);
        result.push({
            group: tab.innerText.trim(),
            hid: hid.id,
            codes: obj.CodeArray.map(function (c) {
                return {name: c.CodeName.trim(), serial: c.SerialNo, depth: c.Depth, parents: c.ParentSerialNo};
            })
        });
    });
});
return result;
"""

JS_INQUIRE_SET_CODES = JS_INQUIRE_CODE_HELPERS + """
var obj = readCode(arguments[0]);
var serials = arguments[1];
[obj.CodeArray, obj.OriginCodeArray].forEach(function (array) {
    (array || []).forEach(function (c) { c.Selected = serials.indexOf(c.SerialNo) > -1; });
});
writeCode(arguments[0], obj);
"""

JS_INQUIRE_ITEMS = JS_INQUIRE_CODE_HELPERS + """
var tree = document.getElementById(arguments[0]);
return Array.prototype.map.call(tree.querySelectorAll('label'), function (label) {
    var box = document.getElementById(label.htmlFor);
    return {name: codeName(label), id: label.htmlFor, checked: box.checked};
});
"""

JS_INQUIRE_PERIOD = """
var prefix = arguments[0], value = arguments[1], isMonth = arguments[2];
var chkYear = document.getElementById(prefix + 'chkYearData');
var chkMonth = document.getElementById(prefix + 'chkMonthData');
var kind = isMonth ? 'Month' : 'Year';
var begin = document.getElementById(prefix + 'ddl' + kind + 'Begin');
var end = document.getElementById(prefix + 'ddl' + kind + 'End');
if (!begin) {
    return {ok: false, missing: true};
}
var options = Array.prototype.map.call(begin.options, function (o) { return o.text.trim(); });
var values = Array.prototype.map.call(begin.options, function (o) { return o.value; });
if (values.indexOf(value) < 0) {
    return {ok: false, options: options};
}
var want = isMonth ? chkMonth : chkYear;
var other = isMonth ? chkYear : chkMonth;
if (want && !want.checked) { want.click(); }
if (other && other.checked) { other.click(); }
begin.value = value;
end.value = value;
return {ok: true};
"""

JS_INQUIRE_TABLE = """
// 把結果表格（含 rowspan/colspan）展開成二維陣列
function expand(rows) {
    var grid = [];
    Array.prototype.forEach.call(rows, function (tr, r) {
        grid[r] = grid[r] || [];
        var c = 0;
        Array.prototype.forEach.call(tr.cells, function (cell) {
            while (grid[r][c] !== undefined) { c++; }
            var text = cell.innerText.replace(/\\u00a0/g, ' ').trim();
            for (var i = 0; i < (cell.rowSpan || 1); i++) {
                for (var j = 0; j < (cell.colSpan || 1); j++) {
                    grid[r + i] = grid[r + i] || [];
                    grid[r + i][c + j] = {text: text, cls: cell.className};
                }
            }
            c += cell.colSpan || 1;
        });
    });
    return grid;
}
var table = document.getElementById(arguments[0]);
if (!table) { return null; }
return {head: expand(table.tHead ? table.tHead.rows : []), body: expand(table.tBodies[0] ? table.tBodies[0].rows : [])};
"""

JS_INQUIRE_MESSAGE = """
var boxes = Array.prototype.filter.call(document.querySelectorAll('.msgBoxContainer'), function (e) {
    return e.offsetParent !== null;
});
return boxes.map(function (e) { return e.innerText.trim(); }).join('\\n');
"""


class InquireAdvanceBasicApiView(BasicApiView):
    """
    農業統計資料查詢（動態查詢）公版 ApiView

    2026 年 agrstat 改版後，每個資料表都有固定的 qcode 網址，例如
    https://agrstat.moa.gov.tw/moasdweb/inquire/InquireAdvance.aspx?qcode=CA02
    子類別只要設定 qcode，再依序呼叫：
        inquire_open() → inquire_dimension()（可多次）→ inquire_items() → inquire_period() → inquire_submit()
    之後用 inquire_records() 取出結果。
    """
    url_inquire = 'https://agrstat.moa.gov.tw/moasdweb/inquire/InquireAdvance.aspx?qcode={}'
    prefix = 'ctl00_ContentPlaceHolder1_ucInquireAdvance_'
    qcode = ''

    def inquire_id(self, name):
        return f'{self.prefix}{name}'

    def inquire_wait_ready(self):
        WebDriverWait(self.driver, 30, 0.2).until(EC.presence_of_element_located((By.ID, self.inquire_id('btnInquire'))))
        WebDriverWait(self.driver, 30, 0.2).until(lambda d: d.execute_script("return typeof DecryptCode === 'function'"))

    def inquire_postback(self, name):
        """按下會整頁送出的按鈕，等新頁面載入完成"""
        old_html = self.driver.find_element(By.TAG_NAME, 'html')
        self.driver.execute_script("var b = document.getElementById(arguments[0]); setTimeout(function () { b.click(); }, 0);", self.inquire_id(name))

        def done(driver):
            try:
                old_html.tag_name
            except Exception:
                return 'reload'
            if driver.execute_script(JS_INQUIRE_MESSAGE):
                return 'message'
            return False

        state = WebDriverWait(self.driver, 60, 0.2).until(done)
        if state == 'message':
            message = self.driver.execute_script(JS_INQUIRE_MESSAGE)
            self.message = f'「{self.command_text}」查詢失敗：{message}'
            raise CustomError(self.message)
        self.inquire_wait_ready()

    def inquire_open(self, qcode=None):
        if not getattr(self, 'driver', None):
            self.driver = get_driver()
        self.driver.get(self.url_inquire.format(qcode or self.qcode))
        self.inquire_wait_ready()

    @staticmethod
    def match_names(options, keyword, multiple=False):
        """
        從選項名稱中找出符合關鍵字的項目
        完全符合優先，其次是包含關鍵字；multiple=False 時只取第一個
        """
        keyword = keyword.replace('台', '臺')
        exact = [o for o in options if o['name'].replace('台', '臺') == keyword]
        matched = exact or [o for o in options if keyword in o['name'].replace('台', '臺')]
        return matched if multiple else matched[:1]

    def inquire_dimensions(self):
        return self.driver.execute_script(JS_INQUIRE_DIMENSIONS, self.prefix)

    def inquire_dimension(self, selections):
        """
        設定複分類的選項
        selections: {分類名稱: [關鍵字, ...] 或 None（全選）}，關鍵字找不到時拋出 CustomError
        回傳 {分類名稱: [實際選到的名稱, ...]}
        """
        dimensions = self.inquire_dimensions()
        picked = dict()
        for group, keywords in selections.items():
            dimension = next((d for d in dimensions if d['group'] == group), None)
            if dimension is None:
                raise Exception(f'qcode={self.qcode} 找不到分類「{group}」，網站可能改版')
            if keywords is None:
                codes = dimension['codes']
            else:
                codes = list()
                for keyword in keywords:
                    matched = self.match_names(dimension['codes'], keyword, multiple=getattr(self, 'match_multiple', False))
                    if not matched:
                        self.message = f'查無{group}「{keyword}」'
                        raise CustomError(self.message)
                    codes += [c for c in matched if c not in codes]
            self.driver.execute_script(JS_INQUIRE_SET_CODES, dimension['hid'], [c['serial'] for c in codes])
            picked[group] = [c['name'] for c in codes]
        self.inquire_postback('btnSaveItemDimension')
        return picked

    def inquire_items(self, names=None):
        """勾選統計量；names 為 None 時全選"""
        items = self.driver.execute_script(JS_INQUIRE_ITEMS, self.inquire_id('ucItemCode_panCodeTree'))
        if names is None:
            targets = items
        else:
            targets = list()
            for name in names:
                matched = self.match_names(items, name)
                if not matched:
                    raise Exception(f'qcode={self.qcode} 找不到統計量「{name}」，網站可能改版')
                targets += matched
        for item in targets:
            if not item['checked']:
                self.driver.execute_script("document.getElementById(arguments[0]).click();", item['id'])
        return [item['name'] for item in targets]

    def inquire_period(self, year, month=None):
        value = f'{int(year):03d}{int(month):02d}' if month else f'{int(year):03d}'
        result = self.driver.execute_script(JS_INQUIRE_PERIOD, self.prefix, value, bool(month))
        if result['ok']:
            return
        if result.get('missing'):
            if month:
                self.message = f'「{self.command_text}」沒有月份的資料，請只輸入年份'
            else:
                self.message = f'「{self.command_text}」沒有年份的資料，請輸入「年份/月份」'
            raise CustomError(self.message)
        options = result['options']
        if month:
            date_start, date_end = [o.replace('月', '').replace('年', '/') for o in (options[0], options[-1])]
        else:
            date_start, date_end = [o.replace('年', '') for o in (options[0], options[-1])]
        self.message = f'日期「{self.query_date}」無效，日期需介於「{date_start}」～「{date_end}」之間'
        raise CustomError(self.message)

    def inquire_submit(self):
        self.inquire_postback('btnInquire')
        WebDriverWait(self.driver, 30, 0.2).until(EC.presence_of_element_located((By.ID, self.inquire_id('tabResult'))))

    def inquire_records(self):
        """
        把結果表格轉成清單，每一格一筆：
        {'side': [表側標題...], 'head': [表頭標題...], 'value': '1,234'}
        表頭標題由上到下，重複的（合併儲存格）只保留一次
        """
        table = self.driver.execute_script(JS_INQUIRE_TABLE, self.inquire_id('tabResult'))
        head, body = table['head'], table['body']
        side_count = sum(1 for cell in head[0] if 'HorVerCross' in cell['cls']) if head else 1

        def dedup(texts):
            result = list()
            for text in texts:
                if text and (not result or result[-1] != text):
                    result.append(text)
            return result

        records = list()
        for row in body:
            side = dedup([cell['text'] for cell in row[:side_count]])
            for col in range(side_count, len(row)):
                path = dedup([head_row[col]['text'] for head_row in head if col < len(head_row) and 'HorDimSep' not in head_row[col]['cls']])
                records.append({'side': side, 'head': path, 'value': row[col]['text']})
        return records

    @staticmethod
    def find_record(records, *keywords):
        """找出表頭（或表側）同時包含所有關鍵字的第一筆資料"""
        for record in records:
            texts = record['head'] + record['side']
            if all(any(keyword == text or keyword in text for text in texts) for keyword in keywords):
                return record
        return None


class ProductCityInquireApiView(InquireAdvanceBasicApiView):
    """
    「指令 品項 年份」或「指令 品項 年份 縣市」的農業統計資料查詢公版
    例如場數、在養量、屠宰量、副產物產量

    子類別設定：
        tables: [(qcode, 品項分類名稱, 統計量名稱), ...]，依序找出含有該品項的資料表
        label: 回覆時的統計量名稱
        usage: 參數錯誤時的用法說明
    """
    tables = []
    label = ''
    usage = ''

    def __init__(self, params):
        self.driver = None
        self.message = ''

        if len(params) not in [3, 4]:
            raise CustomError(self.usage)

        self.command = params[0]
        self.product = params[1]
        self.query_date = params[2]
        self.city = params[3].replace('台', '臺') if len(params) == 4 else None
        self.command_text = ' '.join(text for text in params)

    def find_table(self):
        """開啟含有該品項的資料表，回傳 (品項分類名稱, 統計量名稱)"""
        options = list()
        for qcode, group, item in self.tables:
            self.qcode = qcode
            self.inquire_open()
            dimension = next(d for d in self.inquire_dimensions() if d['group'] == group)
            if self.match_names(dimension['codes'], self.product):
                return group, item
            options += [c['name'] for c in dimension['codes']]
        self.message = f'查無品項「{self.product}」，可查詢的品項如下：\n' + '、'.join(options)
        raise CustomError(self.message)

    def get_data(self):
        group, item = self.find_table()
        selections = {group: [self.product]}
        if self.city is not None:
            selections['縣市別'] = [self.city]
        picked = self.inquire_dimension(selections)
        self.inquire_items([item])
        self.inquire_period(self.year)
        self.inquire_submit()
        record = self.inquire_records()[0]

        # 單位可能在品項名稱「牛乳(公斤)」或統計量表頭「家畜飼養頭數(頭)」
        product = picked[group][0]
        unit = re.search(r'\(([^()]*)\)\s*$', product) or re.search(r'\(([^()]*)\)\s*$', record['head'][0])
        product = re.sub(r'\([^()]*\)\s*$', '', product)
        city = f' {picked["縣市別"][0]}' if self.city is not None else ''
        unit = f'({unit.group(1)})' if unit else ''
        self.message = f'{self.year}年 {product}{city} {self.label}：{record["value"]}{unit}'
