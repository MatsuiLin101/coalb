from .configs import *


class CropPriceBuilder(object):
    '''
from apps.coa.builders.cropprice import *
a = CropPriceBuilder()
    '''
    def __init__(self):
        self.driver = None
        self.url = "https://apis.afa.gov.tw/pagepub/AppContentPage.aspx?itemNo=PRI105"
        self.id_category = "WR1_1_Q_GroupCode_XX_C1"
        self.id_table = "WR1_1_PRMG_0_X"

    def build(self):
        CropPrice.objects.all().delete()
        self.driver = get_driver(False)
        self.driver.get(self.url)
        # 進入農糧署農產品產地價格查報系統
        select_category = self.driver.find_element(By.ID, self.id_category)
        options = select_category.find_elements(By.TAG_NAME, "option")
        count_option = 0
        count_table = 0
        while count_option < len(options):
            select_category = self.driver.find_element(By.ID, self.id_category)
            option = select_category.find_elements(By.TAG_NAME, "option")[count_option]
            count_option += 1
            count_table += 1
            category = option.text
            id_table = self.id_table.replace('_X', f'{count_table}')
            driver_select(self.driver, self.id_category, "text", category)
            WebDriverWait(self.driver, 30, 0.1).until(EC.presence_of_element_located((By.ID, id_table)))

            table = self.driver.find_element(By.ID, id_table)
            tds = table.find_elements(By.TAG_NAME, 'td')
            for td in tds:
                name = td.text
                if len(name) == 0:
                    continue
                input = td.find_element(By.TAG_NAME, 'input')
                value = input.get_attribute('value')
                code = input.get_attribute('id')
                obj = CropPrice.objects.create(category=category, id_table=id_table, value=value, code=code, name=name)
                print(f'create {category} {obj}')
        self.driver.close()

    def close(self):
        self.driver.close()
