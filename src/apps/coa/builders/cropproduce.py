from .configs import *


class CropProduceTotalBuilder(object):
    '''
from apps.coa.builders.cropproduce import *
a = CropProduceTotalBuilder()
    '''
    def __init__(self):
        self.driver = None
        self.url = "https://agr.afa.gov.tw/afa/afa_frame.jsp"
        self.frame_left = "/html/frameset/frameset/frame[1]"
        self.frame_right = "/html/frameset/frameset/frame[2]"
        self.menu1 = "/html/body/div/div/div[1]/a"
        self.menu2 = "/html/body/div/div/div[2]/a"
        self.menu3 = "/html/body/div/div/div[3]/a"
        self.select_year = "/html/body/div/form/div/table/tbody/tr[1]/td[2]/select"
        # self.select_product = "/html/body/div/form/div/table/tbody/tr[3]/td[2]/select"
        self.select_product = "/html/body/div/form/div/table/tbody/tr[4]/td[2]/select"
        # self.select_city = "/html/body/div/form/div/table/tbody/tr[4]/td[2]/select"
        self.select_city = "/html/body/div/form/div/table/tbody/tr[5]/td[2]/select"
        # self.btn_query = "/html/body/div/form/div/table/tbody/tr[5]/td[2]/input[1]"
        self.btn_query = "/html/body/div/form/div/table/tbody/tr[6]/td[2]/input[1]"
        self.table = "/html/body/div/form/div/table"

    def build(self):
        CropProduceTotal.objects.all().delete()
        self.driver = get_driver()
        self.driver.get(self.url)
        # 進入農糧署農情報告資源網
        frame_left = self.driver.find_element(By.XPATH, self.frame_left)
        frame_right = self.driver.find_element(By.XPATH, self.frame_right)
        self.driver.switch_to_frame(frame_left)
        self.driver.find_element(By.XPATH, self.menu1).click()
        self.driver.find_element(By.XPATH, self.menu2).click()
        self.driver.find_element(By.XPATH, self.menu3).click()
        self.driver.switch_to_default_content()
        self.driver.switch_to_frame(frame_right)

        select_product = self.driver.find_element(By.XPATH, self.select_product)
        options = select_product.find_elements(By.TAG_NAME, 'option')
        for option in options:
            name = option.text
            value = option.get_attribute('value')
            obj = CropProduceTotal.objects.create(name=name, value=value)
            print(f"Create {obj} {name} {value}")

        self.driver.close()
