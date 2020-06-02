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


BOOK_DICT = {
    '產值': 'ctl00_cphMain_uctlBook_repChapter_ctl06_dtlFile_ctl00_lnkFile',
    '農家所得': 'ctl00_cphMain_uctlBook_repChapter_ctl30_dtlFile_ctl00_lnkFile',
    '農牧戶': 'ctl00_cphMain_uctlBook_repChapter_ctl28_dtlFile_ctl00_lnkFile',
    '耕地面積': 'ctl00_cphMain_uctlBook_repChapter_ctl52_dtlFile_ctl00_lnkFile',
}


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
        if len(split) == 2:
            return pre_process_text_2(split_text)
        elif len(split) == 3:
            return pre_process_text_3(split_text)
        else:
            return 'pre_process_text 輸入錯誤'
    except Exception as e:
        return  'pre_process_text 發生錯誤'



def pre_process_text_2(split_text):
    year = split_text[0]
    key = split_text[1]
    if '農家所得' in key:
        return get_book_income(year, key)
    elif '農牧戶' in key:
        return get_book_farmercount(year, key)
    elif '耕地面積' in key:
        return get_book_farmarea(year, key)


def pre_process_text_3(split_text):
    year = split_text[0]
    key = split_text[1]
    value = split_text[-1]
    if '產值' in key:
        return get_book_value(year, key, value)


def get_book(key):
    chrome = 'chromedriver'
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
        return '發生錯誤'


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
        return '發生錯誤'


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
        return '發生錯誤'


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
        return '發生錯誤'
