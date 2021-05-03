import os

from apps.coa.utils import *


class ApiView(object):
    '''
    Basic view for coa apis
    '''
    def __init__(self, url, key, year, product='', city=''):
        self.url = url
        self.key = key
        self.year = year
        self.product = product
        self.city = city

    def download(self):
        # download ods and transfer to xlsx
        driver = get_driver()
        try:
            driver.get(self.url)
            WebDriverWait(driver, 30, 0.1).until(EC.presence_of_element_located((By.ID, self.id_book)))
            driver.find_element(By.ID, self.id_book).click()
            ods = driver.find_element(By.ID, self.id_ods)
            ods_href = ods.get_attribute("href")

            ods_name = f"value_{int(datetime.datetime.now().timestamp())}.ods"
            res = requests.get(ods_href)
            with open(ods_name, 'wb') as f:
                f.write(res.content)
            subprocess.Popen(f'{settings.LIBREOFFICE_PATH} --headless --invisible --convert-to xlsx {ods_name}', shell=True, stderr=subprocess.PIPE).communicate()
            self.xlsx_name = ods_name.replace('ods', 'xlsx')
            os.remove(ods_name)
        except Exception as e:
            print(e)
        driver.close()
