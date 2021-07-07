import os
import traceback

from apps.log.models import TracebackLog

from apps.coa.utils import *
from apps.coa.models import *


class BasicApiView(object):
    '''
    Basic view for coa apis
    '''
    def __init__(self, url, key, year, product='', city=''):
        self.url = url
        self.key = key
        self.year = year
        self.product = product
        self.city = city

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
            pass
        except Exception as e:
            traceback_log = TracebackLog.objects.create(app=f"{self.classname}", message=traceback.format_exc())
            self.message = f"發生錯誤，請通知管理員處理，錯誤編號「{traceback_log.id}」"
        if self.driver:
            self.driver.close()
        return self.message

    def download(self):
        # download ods and transfer to xlsx
        driver = get_driver()
        try:
            driver.get(self.url)
            WebDriverWait(driver, 30, 0.1).until(EC.presence_of_element_located((By.ID, self.id_book)))
            driver.find_element(By.ID, self.id_book).click()
            ods = driver.find_element(By.ID, self.id_ods)
            ods_href = ods.get_attribute("href")

            ods_name = f"ods_{int(datetime.datetime.now().timestamp())}.ods"
            res = requests.get(ods_href)
            with open(ods_name, 'wb') as f:
                f.write(res.content)
            subprocess.Popen(f'{settings.LIBREOFFICE_PATH} --headless --invisible --convert-to xlsx {ods_name}', shell=True, stderr=subprocess.PIPE).communicate()
            self.xlsx_name = ods_name.replace('.ods', '.xlsx')
            os.remove(ods_name)
        except Exception as e:
            print(e)
        driver.close()


class CustomError(Exception):
    pass
