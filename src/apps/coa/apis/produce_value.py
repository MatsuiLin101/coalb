import json
import re
import requests

from bs4 import BeautifulSoup as bs
from decimal import Decimal
from openpyxl import load_workbook
from pyexcel_ods import get_data
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support.ui import Select

# from apps.coas.apis.produce_value import main
def main(city='新北市', year=106):

    # chrome = '/usr/bin/chromedriver'
    chrome = '/Users/coder/.rvm/gems/ruby-2.5.1/bin/chromedriver'
    chrome_options = Options()
    # chrome_options.add_argument('--headless')
    chrome_options.add_argument('User-Agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.70 Safari/537.36"')
    driver = webdriver.Chrome(executable_path=chrome, options=chrome_options)
    url = 'https://agrstat.coa.gov.tw/sdweb/public/inquiry/InquireAdvance.aspx'
    driver.get(url)

    # enter product value main page
    main_xpath = '/html/body/form/div[4]/table/tbody/tr/td/table/tbody/tr[6]/td[2]/a[1]'
    main_locator = (By.XPATH, main_xpath)
    WebDriverWait(driver, 10, 0.1).until(EC.presence_of_element_located(main_locator)).click()

    # select product value
    category_xpath = '/html/body/form/div[4]/table/tbody/tr[2]/td[2]/div/select/option[4]'
    category_locator = (By.XPATH, category_xpath)
    WebDriverWait(driver, 10, 0.1).until(EC.presence_of_element_located(category_locator)).click()

    # deselect city
    city_id = 'ctl00_cphMain_uctlInquireAdvance_dtlDimension_ctl00_lstDimension'
    city_id_locator = (By.ID, city_id)
    city_select = Select(WebDriverWait(driver, 10, 0.1).until(EC.presence_of_element_located(city_id_locator)))
    city_select.deselect_all()

    # select city
    city_options = {
        '合計': '/html/body/form/div[4]/table/tbody/tr[5]/td[2]/div/table/tbody/tr/td[1]/select/option[1]',
        '新北市': '/html/body/form/div[4]/table/tbody/tr[5]/td[2]/div/table/tbody/tr/td[1]/select/option[2]',
        '台北市': '/html/body/form/div[4]/table/tbody/tr[5]/td[2]/div/table/tbody/tr/td[1]/select/option[3]',
        '桃園市': '/html/body/form/div[4]/table/tbody/tr[5]/td[2]/div/table/tbody/tr/td[1]/select/option[4]',
        '台中市': '/html/body/form/div[4]/table/tbody/tr[5]/td[2]/div/table/tbody/tr/td[1]/select/option[5]',
        '台南市': '/html/body/form/div[4]/table/tbody/tr[5]/td[2]/div/table/tbody/tr/td[1]/select/option[6]',
        '高雄市': '/html/body/form/div[4]/table/tbody/tr[5]/td[2]/div/table/tbody/tr/td[1]/select/option[7]',
        '台北縣': '/html/body/form/div[4]/table/tbody/tr[5]/td[2]/div/table/tbody/tr/td[1]/select/option[11]',
        '宜蘭縣': '/html/body/form/div[4]/table/tbody/tr[5]/td[2]/div/table/tbody/tr/td[1]/select/option[12]',
        '桃園縣': '/html/body/form/div[4]/table/tbody/tr[5]/td[2]/div/table/tbody/tr/td[1]/select/option[13]',
        '新竹縣': '/html/body/form/div[4]/table/tbody/tr[5]/td[2]/div/table/tbody/tr/td[1]/select/option[14]',
        '苗栗縣': '/html/body/form/div[4]/table/tbody/tr[5]/td[2]/div/table/tbody/tr/td[1]/select/option[15]',
        '台中縣': '/html/body/form/div[4]/table/tbody/tr[5]/td[2]/div/table/tbody/tr/td[1]/select/option[16]',
        '彰化縣': '/html/body/form/div[4]/table/tbody/tr[5]/td[2]/div/table/tbody/tr/td[1]/select/option[17]',
        '南投縣': '/html/body/form/div[4]/table/tbody/tr[5]/td[2]/div/table/tbody/tr/td[1]/select/option[18]',
        '雲林縣': '/html/body/form/div[4]/table/tbody/tr[5]/td[2]/div/table/tbody/tr/td[1]/select/option[19]',
        '嘉義縣': '/html/body/form/div[4]/table/tbody/tr[5]/td[2]/div/table/tbody/tr/td[1]/select/option[20]',
        '台南縣': '/html/body/form/div[4]/table/tbody/tr[5]/td[2]/div/table/tbody/tr/td[1]/select/option[21]',
        '高雄縣': '/html/body/form/div[4]/table/tbody/tr[5]/td[2]/div/table/tbody/tr/td[1]/select/option[22]',
        '屏東縣': '/html/body/form/div[4]/table/tbody/tr[5]/td[2]/div/table/tbody/tr/td[1]/select/option[23]',
        '台東縣': '/html/body/form/div[4]/table/tbody/tr[5]/td[2]/div/table/tbody/tr/td[1]/select/option[24]',
        '花蓮縣': '/html/body/form/div[4]/table/tbody/tr[5]/td[2]/div/table/tbody/tr/td[1]/select/option[25]',
        '澎湖縣': '/html/body/form/div[4]/table/tbody/tr[5]/td[2]/div/table/tbody/tr/td[1]/select/option[26]',
        '基隆市': '/html/body/form/div[4]/table/tbody/tr[5]/td[2]/div/table/tbody/tr/td[1]/select/option[27]',
        '新竹市': '/html/body/form/div[4]/table/tbody/tr[5]/td[2]/div/table/tbody/tr/td[1]/select/option[28]',
        '台中市': '/html/body/form/div[4]/table/tbody/tr[5]/td[2]/div/table/tbody/tr/td[1]/select/option[29]',
        '嘉義市': '/html/body/form/div[4]/table/tbody/tr[5]/td[2]/div/table/tbody/tr/td[1]/select/option[30]',
        # '台南市': '/html/body/form/div[4]/table/tbody/tr[5]/td[2]/div/table/tbody/tr/td[1]/select/option[31]',
        '金門縣': '/html/body/form/div[4]/table/tbody/tr[5]/td[2]/div/table/tbody/tr/td[1]/select/option[33]',
        '連江縣': '/html/body/form/div[4]/table/tbody/tr[5]/td[2]/div/table/tbody/tr/td[1]/select/option[34]',
    }
    city_option_xpath = '/html/body/form/div[4]/table/tbody/tr[5]/td[2]/div/table/tbody/tr/td[1]/select/option[2]'
    city_option_locator = (By.XPATH, city_option_xpath)
    WebDriverWait(driver, 10, 0.1).until(EC.presence_of_element_located(city_option_locator)).click()

    data = dict()
    product_options = {
        '合計': '/html/body/form/div[4]/table/tbody/tr[5]/td[2]/div/table/tbody/tr/td[3]/select/option[1]',
        '農產': '/html/body/form/div[4]/table/tbody/tr[5]/td[2]/div/table/tbody/tr/td[3]/select/option[2]',
        '林產': '/html/body/form/div[4]/table/tbody/tr[5]/td[2]/div/table/tbody/tr/td[3]/select/option[3]',
        '畜產': '/html/body/form/div[4]/table/tbody/tr[5]/td[2]/div/table/tbody/tr/td[3]/select/option[4]',
        '漁產': '/html/body/form/div[4]/table/tbody/tr[5]/td[2]/div/table/tbody/tr/td[3]/select/option[5]',
    }
    for key, value in product_options.items():
        # deselect Product
        product_id = 'ctl00_cphMain_uctlInquireAdvance_dtlDimension_ctl02_lstDimension'
        product_locator = (By.ID, product_id)
        product_select = Select(WebDriverWait(driver, 10, 0.1).until(EC.presence_of_element_located(product_locator)))
        product_select.deselect_all()

        # select product
        product_option_xpath = value
        product_option_locator = (By.XPATH, product_option_xpath)
        WebDriverWait(driver, 10, 0.1).until(EC.presence_of_element_located(product_option_locator)).click()

        # submit query
        submit_id = 'ctl00_cphMain_uctlInquireAdvance_btnQuery'
        submit_locator = (By.ID, submit_id)
        WebDriverWait(driver, 10, 0.1).until(EC.presence_of_element_located(submit_locator)).click()

        # set begin and end year the same
        try:
            year_start_id = 'ctl00_cphMain_uctlInquireAdvance_ddlYearBegin'
            year_start_locator = (By.ID, year_start_id)
            year_start_select = Select(WebDriverWait(driver, 10, 0.1).until(EC.presence_of_element_located(year_start_locator)))
            year_start_select.select_by_value(str(year).zfill(3))
            year_end_id = 'ctl00_cphMain_uctlInquireAdvance_ddlYearEnd'
            year_end_locator = (By.ID, year_end_id)
            year_end_select = Select(WebDriverWait(driver, 10, 0.1).until(EC.presence_of_element_located(year_end_locator)))
            year_end_select.select_by_value(str(year).zfill(3))
        except Exception as e:
            data.update({key: f"無{year}年資料"})
            back_id = 'ctl00_cphMain_uctlInquireAdvance_btnBack2'
            back_locator = (By.ID, back_id)
            WebDriverWait(driver, 10, 0.1).until(EC.presence_of_element_located(back_locator)).click()
            continue

        # submit new year interval
        submit2_id = 'ctl00_cphMain_uctlInquireAdvance_btnQuery2'
        submit2_locator = (By.ID, submit2_id)
        WebDriverWait(driver, 10, 0.1).until(EC.presence_of_element_located(submit2_locator)).click()
        while True:
            table_id = 'ctl00_cphMain_uctlInquireAdvance_tabResult'
            table_locator = (By.ID, table_id)
            table = WebDriverWait(driver, 10, 0.1).until(EC.presence_of_element_located(table_locator))
            if len(table.text.split('\n')) <= 4:
                break
        # result_xpath = '/html/body/form/div[4]/table[3]/tbody/tr[2]/td[2]/div/table/tbody/tr[4]/td[2]'
        # result_locator = (By.XPATH, result_xpath)
        # result = WebDriverWait(driver, 10, 0.1).until(EC.presence_of_element_located(result_locator)).text
        result = table.text.split('\n')[-1].replace(f'{year}年 ', '')
        data.update({key: f"{result}(仟元)"})

        back_id = 'ctl00_cphMain_uctlInquireAdvance_btnBack2'
        back_locator = (By.ID, back_id)
        WebDriverWait(driver, 10, 0.1).until(EC.presence_of_element_located(back_locator)).click()

    print(data)
    driver.close()
