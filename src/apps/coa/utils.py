import time
import json
import re
import requests
import traceback

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

from apps.coa.models import *


BOOK_DICT = {
    '產值': 'ctl00_cphMain_uctlBook_repChapter_ctl06_dtlFile_ctl00_lnkFile',
    '農家所得': 'ctl00_cphMain_uctlBook_repChapter_ctl30_dtlFile_ctl00_lnkFile',
    '農牧戶': 'ctl00_cphMain_uctlBook_repChapter_ctl28_dtlFile_ctl00_lnkFile',
    '耕地面積': 'ctl00_cphMain_uctlBook_repChapter_ctl52_dtlFile_ctl00_lnkFile',
}


def main(city, year):
    city = city.replace("台", "臺")
    try:
        print(query_produce_value(city, f"{year}").strip())
    except Exception as e:
        print(traceback.format_exc())


def get_driver(url, headless=True):
    """
    取得selenium驅動瀏覽器
    url: 目標網址
    headless: True為啟動無頭模式(不會開啟瀏覽器， 只會在背景運行)
    """
    chrome = '/Users/coder/Desktop/chrome/chromedriver'
    chrome_options = Options()
    if headless:
        chrome_options.add_argument('--headless')
    chrome_options.add_argument('User-Agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.70 Safari/537.36"')
    driver = webdriver.Chrome(executable_path=chrome, options=chrome_options)
    driver.get(url)
    return driver


def driver_select(driver, id, method, target, cancel=False):
    """
    根據條件選取select物件的內容
    driver: selenium瀏覽器
    id: select物件的id
    method: selenium選取物件的方式
    target: selenium要選取的value或text
    cancel: select為multiple時可使用，True取消原本已選取的項目
    """
    time.sleep(1)
    WebDriverWait(driver, 30, 0.1).until(EC.presence_of_element_located((By.ID, id)))
    select = Select(driver.find_element(By.ID, id))
    if cancel:
        select.deselect_all()
    if method == "value":
        select.select_by_value(target)
    elif method == "text":
        select.select_by_visible_text(target)


def query_produce_value(city, year):
    '''
    爬取動態查詢總產值/產值資料
    '''
    url = "https://agrstat.coa.gov.tw/sdweb/public/inquiry/InquireAdvance.aspx"
    text_title = "農業產值結構與指標"
    text_group = "農業產值：縣市別×農業別"
    id_group = "ctl00_cphMain_uctlInquireAdvance_lstFieldGroup"
    id_city = "ctl00_cphMain_uctlInquireAdvance_dtlDimension_ctl00_lstDimension"
    id_category = "ctl00_cphMain_uctlInquireAdvance_dtlDimension_ctl02_lstDimension"
    id_search = "ctl00_cphMain_uctlInquireAdvance_btnQuery"
    id_start = "ctl00_cphMain_uctlInquireAdvance_ddlYearBegin"
    id_end = "ctl00_cphMain_uctlInquireAdvance_ddlYearEnd"
    id_query = "ctl00_cphMain_uctlInquireAdvance_btnQuery2"
    id_table = "ctl00_cphMain_uctlInquireAdvance_tabResult"
    id_back = "ctl00_cphMain_uctlInquireAdvance_btnBack2"
    message = ""

    if "臺中市" in city or "臺南市" in city:
        if "省" in city:
            name = city.split("省")[-1]
            province = "臺灣省"
        else:
            name = city
            province = str()
        query_set = ProduceValueCity.objects.filter(name=name, province=province)
    else:
        query_set = ProduceValueCity.objects.filter(name__icontains=city)
    count = query_set.count()
    if count == 0:
        return f"查無「{city}」的資料"
    elif count >= 2:
        message += f"搜尋「{city}」出現以下選項，請輸入完整名稱來查詢。\n"
        for obj in query_set:
            message += f"{obj.name}\n" if "臺中市" != obj.name and "臺南市" != obj.name else f"{obj.province}{obj.name}\n"
        return message
    else:
        obj = query_set.first()

    driver = get_driver(url)
    # 進入產值頁面
    driver.find_element(By.LINK_TEXT, text_title).click()

    # 選取產值選項
    driver_select(driver, id_group, "text", text_group)

    # 選取城市
    value_city = obj.value
    driver_select(driver, id_city, "value", value_city, True)
    message += f"{city} {year}年\n"

    message_temp = str()
    categories = ProduceValueFarmCategory.objects.all()
    try:
        for category in categories:
            value_category = category.value
            # 選取屬性
            driver_select(driver, id_category, "value", value_category, True)

            btn_search = driver.find_element(By.ID, id_search)
            btn_search.click()

            # 選擇要查詢的年份
            driver_select(driver, id_start, "value", str(year).zfill(3))
            driver_select(driver, id_end, "value", str(year).zfill(3))

            btn_query = driver.find_element(By.ID, id_query)
            btn_query.click()

            # 取得查詢結果
            WebDriverWait(driver, 30, 0.1).until(EC.presence_of_element_located((By.ID, id_table)))
            table = driver.find_element(By.ID, id_table)
            unit = table.find_element(By.XPATH, 'tbody/tr[1]/td').text.split("產值")[-1]
            value = driver.find_element(By.CSS_SELECTOR, ".VerDim").parent.find_element(By.CSS_SELECTOR, ".ValueLeftTop").text
            message_temp += f"{category.name}：{value}{unit}\n"

            btn_back = driver.find_element(By.ID, id_back)
            btn_back.click()
    except Exception as e:
        message_temp += "查無資料。"

    driver.close()
    message += message_temp
    return message


def query_produce_value_product(product, year, city=None):
    """
    爬取動態查詢作物/畜禽生產量值
    """
    url = "https://agrstat.coa.gov.tw/sdweb/public/inquiry/InquireAdvance.aspx"
    id_group = "ctl00_cphMain_uctlInquireAdvance_lstFieldGroup"
    id_city = "ctl00_cphMain_uctlInquireAdvance_dtlDimension_ctl00_lstDimension"
    id_search = "ctl00_cphMain_uctlInquireAdvance_btnQuery"
    id_start = "ctl00_cphMain_uctlInquireAdvance_ddlYearBegin"
    id_end = "ctl00_cphMain_uctlInquireAdvance_ddlYearEnd"
    id_query = "ctl00_cphMain_uctlInquireAdvance_btnQuery2"
    id_table = "ctl00_cphMain_uctlInquireAdvance_tabResult"
    id_back = "ctl00_cphMain_uctlInquireAdvance_btnBack2"
    product_dict = {
        "rice": {
            "text_title":"農產品生產量值統計" ,
            "text_group": "稻米產值：縣市別×期作別×稻種別",
            "id_category": "ctl00_cphMain_uctlInquireAdvance_dtlDimension_ctl04_lstDimension",
        },
        "grain": {
            "text_title":"農產品生產量值統計" ,
            "text_group": "雜糧產值：縣市別×雜糧別",
            "id_category": "ctl00_cphMain_uctlInquireAdvance_dtlDimension_ctl02_lstDimension",
        },
        "special": {
            "text_title":"農產品生產量值統計" ,
            "text_group": "特作產值：縣市別×特作別",
            "id_category": "ctl00_cphMain_uctlInquireAdvance_dtlDimension_ctl02_lstDimension",
        },
        "sugar": {
            "text_title":"農產品生產量值統計" ,
            "text_group": "製糖甘蔗產值：縣市別",
            "id_category": "",
        },
        "tobacco": {
            "text_title":"農產品生產量值統計" ,
            "text_group": "菸草產值：縣市別",
            "id_category": "",
        },
        "vegetable": {
            "text_title":"農產品生產量值統計" ,
            "text_group": "蔬菜產值：縣市別×蔬菜別",
            "id_category": "ctl00_cphMain_uctlInquireAdvance_dtlDimension_ctl02_lstDimension",
        },
        "mushroom": {
            "text_title":"農產品生產量值統計" ,
            "text_group": "菇類產值：縣市別×菇類別",
            "id_category": "ctl00_cphMain_uctlInquireAdvance_dtlDimension_ctl02_lstDimension",
        },
        "fruits": {
            "text_title":"農產品生產量值統計" ,
            "text_group": "果品產值：縣市別×果品別",
            "id_category": "ctl00_cphMain_uctlInquireAdvance_dtlDimension_ctl02_lstDimension",
        },
        "flower": {
            "text_title":"農產品生產量值統計" ,
            "text_group": "花卉產值：縣市別×花卉別",
            "id_category": "ctl00_cphMain_uctlInquireAdvance_dtlDimension_ctl02_lstDimension",
        },
        "drug": {
            "text_title":"農產品生產量值統計" ,
            "text_group": "藥用產值：縣市別×藥用別",
            "id_category": "ctl00_cphMain_uctlInquireAdvance_dtlDimension_ctl02_lstDimension",
        },
        "livestock": {
            "text_title":"畜禽產品生產量值統計" ,
            "text_group": "家畜產值",
            "id_category": "ctl00_cphMain_uctlInquireAdvance_dtlDimension_ctl02_lstDimension",
        },
        "poultry": {
            "text_title":"畜禽產品生產量值統計" ,
            "text_group": "家禽產值：縣市別×家禽別(104年起)",
            "id_category": "ctl00_cphMain_uctlInquireAdvance_dtlDimension_ctl02_lstDimension",
        },
        "byproduct": {
            "text_title":"畜禽產品生產量值統計" ,
            "text_group": "畜禽副產品產值",
            "id_category": "ctl00_cphMain_uctlInquireAdvance_dtlDimension_ctl02_lstDimension",
        },
        "bee": {
            "text_title":"畜禽產品生產量值統計" ,
            "text_group": "蜂蠶飼養產值",
            "id_category": "ctl00_cphMain_uctlInquireAdvance_dtlDimension_ctl02_lstDimension",
        },
    }
    message = ""

    # 選取產品
    query_set = ProduceValueProduct.objects.filter(name__icontains=product)
    count = query_set.count()
    if count == 0:
        return f"查無「{product}」的資料"
    elif count >= 2:
        qs = query_set.filter(name=product)
        if qs.count() > 0:
            message += f"搜尋「{product}」出現以下選項，將為您查詢「{product}」，若要查詢其他品項，請輸入完整名稱來查詢。\n"
            for obj in query_set:
                message += f"{obj.name}\n"
            obj_product = qs.first()
        else:
            message += f"搜尋「{product}」出現以下選項，請輸入完整名稱來查詢。\n"
            for obj in query_set:
                message += f"{obj.name}\n"
            return message
    else:
        obj_product = query_set.first()

    # 選取城市
    if city:
        if "臺中市" in city or "臺南市" in city:
            if "省" in city:
                name = city.split("省")[-1]
                province = "臺灣省"
            else:
                name = city
                province = str()
            query_set = ProduceValueCity.objects.filter(name=name, province=province, type=obj_product.city_type)
        else:
            query_set = ProduceValueCity.objects.filter(name__icontains=city, type=obj_product.city_type)
        count = query_set.count()
        if count == 0:
            return f"查無「{city}」的資料"
        elif count >= 2:
            message += f"搜尋「{city}」出現以下選項，請輸入完整名稱來查詢。\n"
            for obj in query_set:
                message += f"{obj.name}\n" if "臺中市" != obj.name and "臺南市" != obj.name else f"{obj.province}{obj.name}\n"
            return message
        else:
            obj_city = query_set.first()

    data = product_dict[obj_product.category]
    text_title = data["text_title"]
    text_group = data["text_group"]
    id_category = data["id_category"]

    driver = get_driver(url)
    # 進入產值頁面
    driver.find_element(By.LINK_TEXT, text_title).click()

    # 選取產值選項
    driver_select(driver, id_group, "text", text_group)

    # 選取城市
    if city:
        value_city = obj_city.value
        driver_select(driver, id_city, "value", value_city, True)
    # message += f"{city} {year}年\n"

    message_temp = str()
    try:
        value_category = obj_product.value
        # 選取屬性
        driver_select(driver, id_category, "value", value_category, True)

        btn_search = driver.find_element(By.ID, id_search)
        btn_search.click()

        # 選擇要查詢的年份
        driver_select(driver, id_start, "value", str(year).zfill(3))
        driver_select(driver, id_end, "value", str(year).zfill(3))

        btn_query = driver.find_element(By.ID, id_query)
        btn_query.click()

        # 取得查詢結果
        WebDriverWait(driver, 30, 0.1).until(EC.presence_of_element_located((By.ID, id_table)))
        table = driver.find_element(By.ID, id_table)
        unit = table.find_element(By.XPATH, 'tbody/tr[1]/td').text.split("產值")[-1]
        value = driver.find_element(By.CSS_SELECTOR, ".VerDim").parent.find_element(By.CSS_SELECTOR, ".ValueLeftTop").text
        message_temp += f"{obj_product.name}產值：{value}{unit}\n"

        btn_back = driver.find_element(By.ID, id_back)
        btn_back.click()
    except Exception as e:
        print(traceback.format_exc())
        message_temp += "查無資料。"
        return driver

    driver.close()
    message += message_temp
    return message


def intcomma(num):
    if isinstance(num, (int, float, Decimal)):
        num = str(round(num))
    orig = num
    new = re.sub(r"^(-?\d+)(\d{3})", r'\g<1>,\g<2>', orig)
    if orig == new:
        return new
    else:
        return intcomma(new)


def pre_process_text(text):
    try:
        split_text = text.split(' ')
        if len(split_text) == 2:
            return pre_process_text_2(split_text)
        elif len(split_text) == 3:
            return pre_process_text_3(split_text)
        else:
            return False
    except Exception as e:
        return  f'pre_process_text 發生錯誤, {e}'



def pre_process_text_2(split_text):
    year = split_text[0]
    key = split_text[1]
    if '農家所得' in key:
        return get_book_income(year, key)
    elif '農牧戶' in key:
        return get_book_farmercount(year, key)
    elif '耕地面積' in key:
        return get_book_farmarea(year, key)
    else:
        return False


def pre_process_text_3(split_text):
    year = split_text[0]
    key = split_text[1]
    value = split_text[-1]
    if '產值' in key:
        return get_book_value(year, key, value)
    else:
        return False


def get_book(key):
    # chrome = '/usr/bin/chromedriver'
    # chrome = '/Users/coder/Desktop/coa/coalb/chrome/chromedriver'
    # chrome = '/Users/coder/Desktop/chrome/chromedriver'
    chrome = '/code/chrome/chromedriver'
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('User-Agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.70 Safari/537.36"')
    driver = webdriver.Chrome(executable_path=chrome, options=chrome_options)
    url = 'https://agrstat.coa.gov.tw/sdweb/public/book/'
    aspx = 'Book.aspx'

    try:
        driver.get(f'{url}{aspx}')
        btn_link = driver.find_elements_by_id('ctl00_cphMain_uctlBook_grdBook_ctl10_btnBookName')
        btn_link[0].click()
        soup = bs(driver.page_source, 'html.parser')
        a_link = soup.find('a', {'id': BOOK_DICT.get(key)})
        href = a_link.get('href')[2:]
    except Exception as e:
        return (f'發生錯誤 {e}')
    driver.quit()

    res = requests.get(f"{url}{href}")
    with open(f'{key}.ods', 'wb') as f:
        f.write(res.content)
    data = get_data(f"{key}.ods")

    return data


# 農業統計年報 產值
def get_book_value(year, key, value):
    data = get_book(key)
    message = str()
    if value == '總產值':
        for i in data['10_(2)']:
            if len(i) >= 4:
                if f'{i[5]}' == f'產   量':
                    if f'{year}' in i[6]:
                        col = 6
                    if f'{year}' in i[7]:
                        col = 10
                    if f'{year}' in i[9]:
                        col = 15
                    if f'{year}' in i[10]:
                        col = 19
                if f'{i[1]}' == f'農產品生產總值':
                    num = intcomma(i[col])
                    message = f"{year}年 農產總產值：{num}(千元)"
                    break
    else:
        for i in data['10_(2)']:
            if len(i) >= 4:
                if f'{i[5]}' == f'產   量':
                    if f'{year}' in i[6]:
                        col = 8
                    if f'{year}' in i[7]:
                        col = 12
                    if f'{year}' in i[9]:
                        col = 17
                    if f'{year}' in i[10]:
                        col = 21
                if value in f"{i[3]}":
                    num = intcomma(i[col])
                    message = f"{year}年 {value} 產值：{num}(千元)"
                    break
        for i in data['12_(2)']:
            if len(i) >= 4:
                if f'{i[5]}' == f'產   量':
                    if f'{year}' in i[6]:
                        col = 8
                    if f'{year}' in i[7]:
                        col = 12
                    if f'{year}' in i[9]:
                        col = 17
                    if f'{year}' in i[10]:
                        col = 21
                if value in f"{i[3]}":
                    num = intcomma(i[col])
                    message = f"{year}年 {value} 產值：{num}(千元)"
                    break
        for i in data['14_(2)']:
            if len(i) >= 4:
                if f'{i[5]}' == f'產   量':
                    if f'{year}' in i[6]:
                        col = 8
                    if f'{year}' in i[7]:
                        col = 12
                    if f'{year}' in i[9]:
                        col = 17
                    if f'{year}' in i[10]:
                        col = 21
                if value in f"{i[3]}":
                    num = intcomma(i[col])
                    message = f"{year}年 {value} 產值：{num}(千元)"
                    break
        for i in data['16_(2)']:
            if len(i) >= 4:
                if f'{i[5]}' == f'產   量':
                    if f'{year}' in i[6]:
                        col = 8
                    if f'{year}' in i[7]:
                        col = 12
                    if f'{year}' in i[9]:
                        col = 17
                    if f'{year}' in i[10]:
                        col = 21
                if value in f"{i[3]}":
                    num = intcomma(i[col])
                    message = f"{year}年 {value} 產值：{num}(千元)"
                    break
        for i in data['18_(2)']:
            if len(i) >= 4:
                if f'{i[5]}' == f'產   量':
                    if f'{year}' in i[6]:
                        col = 8
                    if f'{year}' in i[7]:
                        col = 12
                    if f'{year}' in i[9]:
                        col = 17
                    if f'{year}' in i[10]:
                        col = 21
                if value in f"{i[3]}":
                    num = intcomma(i[col])
                    message = f"{year}年 {value} 產值：{num}(千元)"
                    break
    if len(message) > 0:
        return message
    else:
        return f'{year}年 {value} 產值 查無資料'


def get_book_income(year, key):
    data = get_book(key)
    message = str()
    for i in data['所得']:
        if len(i) >= 8:
            if f'{i[1]}年' == f'{year}年':
                message = f'{year}年 農家所得：{intcomma(i[5])}(元)\n{year}年 主力農家所得：{intcomma(i[7])}(元)'
    if len(message) > 0:
        return message
    else:
        return f'{year}年 農家所得 查無資料'


def get_book_farmercount(year, key):
    data = get_book(key)
    message = str()
    for i in data['總戶數及人口數_new']:
        if len(i) >= 8:
            if f'{i[1]}年' == f'{year}年':
                message = f'{year}年 農牧戶戶數：{intcomma(i[5])}(戶)\n{year}年 農牧戶人口數：{intcomma(i[6])}(人)'
    if len(message) > 0:
        return message
    else:
        return f'{year}年 農牧戶 查無資料'


def get_book_farmarea(year, key):
    data = get_book(key)
    message = str()
    for i in data['耕地面積']:
        if len(i) >= 8:
            if f'{i[1]}年' == f'{year}年':
                message = f'{year}年 耕地面積：{intcomma(i[3])}(公頃)'
    if len(message) > 0:
        return message
    else:
        return f'{year}年 耕地面積 查無資料'
