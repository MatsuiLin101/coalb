import os
import traceback

from apps.log.models import TracebackLog

from apps.coa.utils import *
from apps.coa.models import *


class BasicApiView(object):
    '''
    Basic view for coa apis
    '''
    def __init__(self, params):
        self.params = params
        self.command_text = " ".join(text for text in params)

    @property
    def classname(self):
        return self.__class__.__name__

    def parser(self):
        self.driver = get_driver()
        self.driver.get(self.url)

    def execute_api(self):
        '''
        execute api
        '''
        try:
            self.verify_date()
            self.get_data()
        except CustomError:
            raise
        except Exception as e:
            traceback_log = TracebackLog.objects.create(app=f"{self.classname}", message=traceback.format_exc())
            self.message = f"「{self.command_text}」發生未知錯誤，錯誤編號「{traceback_log.id}」，請通知管理員處理"
        if self.driver:
            self.driver.close()
        return self.message


class AnnualReportBasicApiView(BasicApiView):
    '''
    年報用公版ApiView
    如果年報持續報錯，或是轉檔失敗，且時間在6~8月左右，可能是年報更新導致抓不到更新的年報
    '''
    def __init__(self, params):
        self.driver = None
        self.url = "https://agrstat.coa.gov.tw/sdweb/public/book/Book.aspx"
        self.id_book = "ctl00_cphMain_uctlBook_grdBook_ctl03_btnBookName"
        self.xlsx_name = ""
        self.message = ""
        self.row = ""
        self.params = params
        self.command_text = " ".join(text for text in params)

    def execute_api(self):
        try:
            self.download()
            self.open_wb()
            self.verify_date()
            self.get_data()
        except CustomError:
            self.driver.close() if self.driver else None
            os.remove(self.xlsx_name) if self.xlsx_name else None
            raise
        except Exception as e:
            traceback_log = TracebackLog.objects.create(app=f"{self.classname}", message=traceback.format_exc())
            self.message = f"「{self.command_text}」發生未知錯誤，錯誤編號「{traceback_log.id}」，請通知管理員處理"
        self.driver.close() if self.driver else None
        os.remove(self.xlsx_name) if self.xlsx_name else None
        return self.message

    def verify_date(self):
        # verify query year
        try:
            self.year = int(self.query_date)
        except Exception as e:
            self.message = f"年份「{self.query_date}」無效，請輸入民國年"
            raise CustomError(self.message)

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

    def open_wb(self):
        # open value xslx
        wb = load_workbook(filename=self.xlsx_name)
        self.ws = wb[wb.sheetnames[0]]

    def download(self):
        # download ods and transfer to xlsx
        self.driver = get_driver()
        try:
            self.driver.get(self.url)
            WebDriverWait(self.driver, 30, 0.1).until(EC.presence_of_element_located((By.ID, self.id_book)))
            self.driver.find_element(By.ID, self.id_book).click()
            ods = self.driver.find_element(By.ID, self.id_ods)
            ods_href = ods.get_attribute("href")

            ods_name = f"ods_{int(datetime.datetime.now().timestamp())}.ods"
            res = requests.get(ods_href)
            with open(ods_name, 'wb') as f:
                f.write(res.content)
            subprocess.Popen(f'{settings.LIBREOFFICE_PATH} --headless --invisible --convert-to xlsx {ods_name}', shell=True, stderr=subprocess.PIPE).communicate()
            self.xlsx_name = ods_name.replace('.ods', '.xlsx')
            os.remove(ods_name)
        except Exception as e:
            raise


class CustomError(Exception):
    pass
