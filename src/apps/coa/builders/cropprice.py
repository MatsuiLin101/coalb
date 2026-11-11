from django.db import transaction
from django.urls import reverse

from core.settings import (
    PROXY_DOMAIN,
    PROXY_TOKEN
)

from apps.coa.builders.configs import *


class CropPriceOriginBuilder(object):
    """
    建立 農耕價格api介面 CropPriceOriginApiView 使用的選項

from apps.coa.builders.cropprice import *
builder = CropPriceOriginBuilder()
builder.build(build_local=True)
    """
    def __init__(self):
        self.driver = None
        self.url = 'https://apis.afa.gov.tw/pagepub/AppContentPage.aspx?itemNo=PRI105'
        self.id_category = 'WR1_1_Q_GroupCode_XX_C1'
        self.id_table = 'WR1_1_PRMG_0_X'
        self.css_query = 'div.CSS_ABS_Normal'

    def build(self, use_proxy=False, build_local=False, *args, **kwargs):
        """
        use_proxy: 是否使用代理伺服器
            True: 使用代理伺服器，代理伺服器抓取資料後回傳
            False: 直接抓取資料，抓取後存入資料庫

        build_local: 是否使用本地資料，
        """
        if use_proxy:
            return self._build()
        elif build_local:
            data = self._build()
        else:
            res = requests.get(f"{PROXY_DOMAIN}{reverse('coa:proxy_build')}?token={PROXY_TOKEN}&api=CropPriceOriginBuilder")
            data = json.loads(res.text)

        with transaction.atomic():
            CropPriceOrigin.objects.all().delete()
            for item in data:
                obj = CropPriceOrigin.objects.create(**item)
                print(f'create {obj.category} {obj}')

    def _build(self):
        try:
            self.driver = get_driver()
            self.driver.get(self.url)

            # 進入農糧署農產品產地價格查報系統
            select_category = self.driver.find_element(By.ID, self.id_category)
            options = select_category.find_elements(By.TAG_NAME, 'option')
            count_option = 0
            count_table = 0
            data = list()
            while count_option < len(options):
                select_category = self.driver.find_element(By.ID, self.id_category)
                option = select_category.find_elements(By.TAG_NAME, 'option')[count_option]
                count_option += 1
                count_table += 1
                category = option.text
                id_table = self.id_table.replace('_X', f'{count_table}')
                driver_select(self.driver, self.id_category, 'text', category)
                WebDriverWait(self.driver, 30, 0.1).until(EC.presence_of_element_located((By.ID, id_table)))

                table = self.driver.find_element(By.ID, id_table)
                query = self.driver.find_element(By.CSS_SELECTOR, self.css_query)
                id_query = query.get_attribute('id')
                tds = table.find_elements(By.TAG_NAME, 'td')
                for td in tds:
                    name = td.text
                    if len(name) == 0:
                        continue
                    input = td.find_element(By.TAG_NAME, 'input')
                    value = input.get_attribute('value')
                    code = input.get_attribute('id')
                    data.append({
                        'category': category,
                        'id_table': id_table,
                        'id_query': id_query,
                        'value': value,
                        'code': code,
                        'name': name
                    })

            return data
        except Exception:
            print(traceback.format_exc())
        finally:
            if self.driver:
                self.driver.quit()
