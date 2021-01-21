from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from apps.coa.utils import get_driver
from apps.coa.models import *


def build_produce_value_city():
    '''
    建立產值表城市資料
    '''
    url = "https://agrstat.coa.gov.tw/sdweb/public/inquiry/InquireAdvance.aspx"
    driver = get_driver()
    driver.get(url)
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
        obj = ProduceValueCity.objects.create(name=name, value=value, province=province)
        print(f"{obj.name} create")


def build_produce_value_category():
    '''
    建立產值表類別資料
    '''
    url = "https://agrstat.coa.gov.tw/sdweb/public/inquiry/InquireAdvance.aspx"
    driver = get_driver()
    driver.get(url)
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
