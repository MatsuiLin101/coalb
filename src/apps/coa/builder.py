import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from apps.coa.utils import get_driver
from apps.coa.models import *


def init_data():
    build_produce_value_city_1()
    build_produce_value_category()
    BuildInit()


def build_produce_value_city_1():
    '''
    建立產值表城市資料
    '''
    url = "https://agrstat.coa.gov.tw/sdweb/public/inquiry/InquireAdvance.aspx"
    driver = get_driver(url)
    # 選擇 農業產值結構與指標
    driver.find_element(By.LINK_TEXT, "農業產值結構與指標").click()

    # 選擇 農業產值：縣市別×農業別
    dropdown = driver.find_element(By.ID, "ctl00_cphMain_uctlInquireAdvance_lstFieldGroup")
    dropdown.find_element(By.XPATH, "//option[. = '農業產值：縣市別×農業別']").click()

    # 抓取所有城市選項
    select_id = "ctl00_cphMain_uctlInquireAdvance_dtlDimension_ctl00_lstDimension"
    WebDriverWait(driver, 30, 0.1).until(EC.presence_of_element_located((By.ID, select_id)))
    select = Select(driver.find_element(By.ID, select_id))

    # 建立城市資料
    ProduceValueCity.objects.all().delete()
    province = str()
    for option in select.options:
        name = option.text
        value = option.get_attribute("value")
        if "省" in name:
            province = name
        obj = ProduceValueCity.objects.create(name=name, value=value, province=province, type=1)
        print(f"{obj.name} create")
    driver.close()
    build_produce_value_city_2()


def build_produce_value_city_2():
    '''
    建立產值表城市資料
    '''
    url = "https://agrstat.coa.gov.tw/sdweb/public/inquiry/InquireAdvance.aspx"
    driver = get_driver(url)
    # 選擇 農業產值結構與指標
    driver.find_element(By.LINK_TEXT, "畜禽產品生產量值統計").click()

    # 選擇 農業產值：縣市別×農業別
    dropdown = driver.find_element(By.ID, "ctl00_cphMain_uctlInquireAdvance_lstFieldGroup")
    dropdown.find_element(By.XPATH, "//option[. = '家畜產值']").click()

    # 抓取所有城市選項
    select_id = "ctl00_cphMain_uctlInquireAdvance_dtlDimension_ctl00_lstDimension"
    WebDriverWait(driver, 30, 0.1).until(EC.presence_of_element_located((By.ID, select_id)))
    select = Select(driver.find_element(By.ID, select_id))

    # 建立城市資料
    province = str()
    for option in select.options:
        name = option.text
        value = option.get_attribute("value")
        if "省" in name:
            province = name
        obj = ProduceValueCity.objects.create(name=name, value=value, province=province, type=2)
        print(f"{obj.name} create")
    driver.close()


def build_produce_value_category():
    '''
    建立產值表類別資料
    '''
    url = "https://agrstat.coa.gov.tw/sdweb/public/inquiry/InquireAdvance.aspx"
    driver = get_driver(url)
    # 選擇 農業產值結構與指標
    driver.find_element(By.LINK_TEXT, "農業產值結構與指標").click()

    # 選擇 農業產值：縣市別×農業別
    dropdown = driver.find_element(By.ID, "ctl00_cphMain_uctlInquireAdvance_lstFieldGroup")
    dropdown.find_element(By.XPATH, "//option[. = '農業產值：縣市別×農業別']").click()

    # 抓取所有類別選項
    select_id = "ctl00_cphMain_uctlInquireAdvance_dtlDimension_ctl02_lstDimension"
    WebDriverWait(driver, 30, 0.1).until(EC.presence_of_element_located((By.ID, select_id)))
    select = Select(driver.find_element(By.ID, select_id))

    # 建立類別資料
    ProduceValueFarmCategory.objects.all().delete()
    for option in select.options:
        name = option.text
        value = option.get_attribute("value")
        obj = ProduceValueFarmCategory.objects.create(name=name, value=value)
        print(f"{obj.name} create")


class BuildInit(object):
    def __init__(self):
        BuildProduceValueProduct().build_model()
        BuildProduceValueProductAnimal().build_model()


class AbstractBuild(object):
    def __init__(self, text_link, model):
        self.driver = get_driver("https://agrstat.coa.gov.tw/sdweb/public/inquiry/InquireAdvance.aspx")
        self.driver.find_element(By.LINK_TEXT, text_link).click()
        self.dropdown = self.driver.find_element(By.ID, "ctl00_cphMain_uctlInquireAdvance_lstFieldGroup")
        self.model = model

    def get_select(self, select_id):
        WebDriverWait(self.driver, 30, 0.1).until(EC.presence_of_element_located((By.ID, select_id)))
        select_obj = Select(self.driver.find_element(By.ID, select_id))
        return select_obj

    def build_obj(self, select_obj, category, city_type):
        for option in select_obj.options:
            name = option.text.replace('*', '')
            value = option.get_attribute("value")
            obj = self.model.objects.create(name=name, value=value, category=category, city_type=city_type)
            print(f"{obj.name} create")

    def build_model(self):
        self.model.objects.all().delete()

    def close(self):
        self.driver.close()


class BuildProduceValueProduct(AbstractBuild):
    '''
    建立產品產值表 作物
    '''
    def __init__(self, text_link="農產品生產量值統計", model=ProduceValueProduct):
        super(BuildProduceValueProduct, self).__init__(text_link, ProduceValueProduct)

    def build_produce_value_product(self, xpath, select_id, category, city_type):
        self.dropdown = self.driver.find_element(By.ID, "ctl00_cphMain_uctlInquireAdvance_lstFieldGroup")
        self.dropdown.find_element(By.XPATH, xpath).click()
        time.sleep(1)
        select_obj = self.get_select(select_id)
        self.build_obj(select_obj, category, city_type)
        time.sleep(1)

    def build_model(self):
        super(BuildProduceValueProduct, self).build_model()
        # 抓取農業產值稻米選項
        xpath = "//option[. = '稻米產值：縣市別×期作別×稻種別']"
        select_id = "ctl00_cphMain_uctlInquireAdvance_dtlDimension_ctl04_lstDimension"
        self.build_produce_value_product(xpath, select_id, "rice", 1)

        # 抓取農業產值雜糧選項
        xpath = "//option[. = '雜糧產值：縣市別×雜糧別']"
        select_id = "ctl00_cphMain_uctlInquireAdvance_dtlDimension_ctl02_lstDimension"
        self.build_produce_value_product(xpath, select_id, "grain", 1)

        # 抓取農業產值特作選項
        xpath = "//option[. = '特作產值：縣市別×特作別']"
        select_id = "ctl00_cphMain_uctlInquireAdvance_dtlDimension_ctl02_lstDimension"
        self.build_produce_value_product(xpath, select_id, "special", 1)

        # 抓取農業產值製糖甘蔗選項
        # xpath = "//option[. = '製糖甘蔗產值：縣市別']"
        # select_id = ""
        # self.build_produce_value_product(xpath, select_id, "sugar")
        obj = self.model.objects.create(name="甘蔗", category="sugar", city_type=1)
        print(f"{obj.name} create")

        # 抓取農業產值菸草選項
        # xpath = "//option[. = '菸草產值：縣市別']"
        # select_id = ""
        # self.build_produce_value_product(xpath, select_id, "tobacco")
        obj = self.model.objects.create(name="菸草", category="tobacco", city_type=1)
        print(f"{obj.name} create")

        # 抓取農業產值蔬菜選項
        xpath = "//option[. = '蔬菜產值：縣市別×蔬菜別']"
        select_id = "ctl00_cphMain_uctlInquireAdvance_dtlDimension_ctl02_lstDimension"
        self.build_produce_value_product(xpath, select_id, "vegetable", 1)

        # 抓取農業產值菇類選項
        xpath = "//option[. = '菇類產值：縣市別×菇類別']"
        select_id = "ctl00_cphMain_uctlInquireAdvance_dtlDimension_ctl02_lstDimension"
        self.build_produce_value_product(xpath, select_id, "mushroom", 1)

        # 抓取農業產值果品選項
        xpath = "//option[. = '果品產值：縣市別×果品別']"
        select_id = "ctl00_cphMain_uctlInquireAdvance_dtlDimension_ctl02_lstDimension"
        self.build_produce_value_product(xpath, select_id, "fruits", 1)

        # 抓取農業產值花卉選項
        xpath = "//option[. = '花卉產值：縣市別×花卉別']"
        select_id = "ctl00_cphMain_uctlInquireAdvance_dtlDimension_ctl02_lstDimension"
        self.build_produce_value_product(xpath, select_id, "flower", 1)

        # 抓取農業產值藥用選項
        xpath = "//option[. = '藥用產值：縣市別×藥用別']"
        select_id = "ctl00_cphMain_uctlInquireAdvance_dtlDimension_ctl02_lstDimension"
        self.build_produce_value_product(xpath, select_id, "drug", 1)
        self.close()


class BuildProduceValueProductAnimal(BuildProduceValueProduct):
    '''
    建立產品產值表 動物
    '''
    def __init__(self, text_link="畜禽產品生產量值統計", model=ProduceValueProduct):
        super(BuildProduceValueProductAnimal, self).__init__(text_link, ProduceValueProduct)

    def build_model(self):
        # 抓取農業產值家畜產值選項
        xpath = "//option[. = '家畜產值']"
        select_id = "ctl00_cphMain_uctlInquireAdvance_dtlDimension_ctl02_lstDimension"
        self.build_produce_value_product(xpath, select_id, "livestock", 2)

        # 抓取農業產值家禽產值選項
        xpath = "//option[. = '家禽產值：縣市別×家禽別(104年起)']"
        select_id = "ctl00_cphMain_uctlInquireAdvance_dtlDimension_ctl02_lstDimension"
        self.build_produce_value_product(xpath, select_id, "poultry", 2)

        # 抓取農業產值家禽產值選項
        xpath = "//option[. = '畜禽副產品產值']"
        select_id = "ctl00_cphMain_uctlInquireAdvance_dtlDimension_ctl02_lstDimension"
        self.build_produce_value_product(xpath, select_id, "byproduct", 2)

        # 抓取農業產值家禽產值選項
        xpath = "//option[. = '蜂蠶飼養產值']"
        select_id = "ctl00_cphMain_uctlInquireAdvance_dtlDimension_ctl02_lstDimension"
        self.build_produce_value_product(xpath, select_id, "bee", 1)
        self.close()
