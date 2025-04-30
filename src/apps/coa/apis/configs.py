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
