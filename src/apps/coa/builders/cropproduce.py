from django.db import transaction
from django.urls import reverse

from core.settings import (
    PROXY_DOMAIN,
    PROXY_TOKEN
)

from apps.coa.builders.configs import *


class CropProduceTotalBuilder(object):
    """
    建立 農耕作物生產api介面 CropProduceApiView 使用的選項

from apps.coa.builders.cropproduce import *
builder = CropProduceTotalBuilder()
builder.build(build_local=True)
    """
    def __init__(self):
        self.driver = None
        self.url = 'https://agr.afa.gov.tw/afa/afa_frame.jsp'
        self.frame_left = '/html/frameset/frameset/frame[1]'
        self.frame_right = '/html/frameset/frameset/frame[2]'
        self.menu1 = '/html/body/div/div/div[1]/a'
        self.menu2 = '/html/body/div/div/div[2]/a'
        self.menu3 = '/html/body/div/div/div[3]/a'
        self.select_year = '/html/body/div/form/div/table/tbody/tr[1]/td[2]/select'
        # self.select_product = '/html/body/div/form/div/table/tbody/tr[3]/td[2]/select'
        self.select_product = '/html/body/div/form/div/table/tbody/tr[4]/td[2]/select'
        # self.select_city = '/html/body/div/form/div/table/tbody/tr[4]/td[2]/select'
        self.select_city = '/html/body/div/form/div/table/tbody/tr[5]/td[2]/select'
        # self.btn_query = '/html/body/div/form/div/table/tbody/tr[5]/td[2]/input[1]'
        self.btn_query = '/html/body/div/form/div/table/tbody/tr[6]/td[2]/input[1]'
        self.table = '/html/body/div/form/div/table'

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
            res = requests.get(f"{PROXY_DOMAIN}{reverse('coa:proxy_build')}?token={PROXY_TOKEN}&api=CropProduceTotalBuilder")
            data = json.loads(res.text)

        with transaction.atomic():
            CropProduceTotal.objects.all().delete()
            for item in data:
                obj = CropProduceTotal.objects.create(**item)
                print(f'create {obj.name} {obj}')

    def _build(self):
        try:
            self.driver = get_driver()
            self.driver.get(self.url)

            # 進入農糧署農情報告資源網
            frame_left = self.driver.find_element(By.XPATH, self.frame_left)
            frame_right = self.driver.find_element(By.XPATH, self.frame_right)
            self.driver.switch_to.frame(frame_left)
            self.driver.find_element(By.XPATH, self.menu1).click()
            self.driver.find_element(By.XPATH, self.menu2).click()
            self.driver.find_element(By.XPATH, self.menu3).click()
            self.driver.switch_to.default_content()
            self.driver.switch_to.frame(frame_right)

            select_product = self.driver.find_element(By.XPATH, self.select_product)
            options = select_product.find_elements(By.TAG_NAME, 'option')
            data = list()
            for option in options:
                name = option.text
                value = option.get_attribute('value')
                data.append({
                    'name': name,
                    'value': value,
                })
                obj = CropProduceTotal.objects.create(name=name, value=value)

            return data
        except Exception:
            print(traceback.format_exc())
        finally:
            if self.driver:
                self.driver.quit()
