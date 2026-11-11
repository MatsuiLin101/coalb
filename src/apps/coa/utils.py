import datetime
import json
import os
import re
import requests
import subprocess
import time
import traceback

from bs4 import BeautifulSoup as bs
from decimal import Decimal
from openpyxl import load_workbook

from selenium import webdriver
from selenium.webdriver import Remote
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support.ui import Select

from core.settings import CHROME_PATH, REMOTE_BROWSER

from apps.log.models import TracebackLog
from apps.user.models import CustomSetting

from apps.coa.models import *


class CustomError(Exception):
    pass


def get_driver(headless=True, use_proxy=False, new_proxy=None):
    """
    取得selenium驅動瀏覽器
    headless: True為啟動無頭模式(不會開啟瀏覽器， 只會在背景運行)
    return driver

    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
    from selenium.webdriver.remote.webdriver import WebDriver
    from selenium.webdriver import Remote

    options = Options()
    options.add_argument('--aggressive-cache-discard')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-setuid-sandbox')
    options.add_argument('--disable-cache')
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disk-cache-size=0')
    options.add_argument('--headless')
    options.add_argument('--window-size=1280,720')
    options.add_argument('--single-process')
    options.add_argument('User-Agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.70 Safari/537.36"')

    driver = WebDriver(
        command_executor='selenium_chromium:4444/wd/hub',
        options=options,
        desired_capabilities=DesiredCapabilities.CHROME,
    )

    # 測試網站
    driver.get('http://www.example.com')
    print(driver.title)
    driver.quit()
    """
    options = Options()
    options.add_argument('--aggressive-cache-discard')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-setuid-sandbox')
    options.add_argument('--disable-cache')
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disk-cache-size=0')
    options.add_argument('--window-size=1280,720')
    options.add_argument('--single-process')
    options.add_argument('User-Agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.70 Safari/537.36"')

    if headless:
        options.add_argument('--headless')

    if use_proxy:
        if new_proxy:
            options.add_argument(f'--proxy-server={new_proxy}')
        else:
            try:
                obj = CustomSetting.objects.get(name='proxy')
            except Exception as e:
                raise CustomError('請通知管理員設定代理再使用此指令')
            options.add_argument(f'--proxy-server={obj.value}')
        options.add_argument('--ignore-ssl-errors=yes')
        options.add_argument('--ignore-certificate-errors')

    # 設定 Docker 中 selenium/standalone-chrome 的 WebDriver URL
    driver = WebDriver(
        command_executor=f"{REMOTE_BROWSER}:4444/wd/hub",  # 根據 Docker 配置調整此 URL
        options=options,
        desired_capabilities=DesiredCapabilities.CHROME,
    )

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
    time.sleep(0.5)
    WebDriverWait(driver, 30, 0.1).until(EC.presence_of_element_located((By.ID, id)))
    select = Select(driver.find_element(By.ID, id))
    if cancel:
        select.deselect_all()
    if method == 'value':
        select.select_by_value(target)
    elif method == 'text':
        select.select_by_visible_text(target)


def driver_select_xpath(driver, xpath, method, target, cancel=False):
    """
    根據條件選取select物件的內容
    driver: selenium瀏覽器
    xpath: select物件的xpath
    method: selenium選取物件的方式
    target: selenium要選取的value或text
    cancel: select為multiple時可使用，True取消原本已選取的項目
    """
    time.sleep(0.5)
    WebDriverWait(driver, 30, 0.1).until(EC.presence_of_element_located((By.XPATH, xpath)))
    select = Select(driver.find_element(By.XPATH, xpath))
    if cancel:
        select.deselect_all()
    if method == 'value':
        select.select_by_value(target)
    elif method == 'text':
        select.select_by_visible_text(target)


def parse_table_by_header(html):
    """
    依欄位標題讀取 HTML 表格，取代用固定 XPath 指定第幾欄，網站調整欄位順序時也能讀對
    支援 rowspan/colspan 的多層標題，上下層標題以「/」串接，例如「規格豬/平均價格」
    html: 表格的 HTML（例如 selenium 元素的 outerHTML）
    return: 每一列資料一個 dict，key 是欄位標題，value 是儲存格文字
    """
    soup = bs(html, 'html.parser')
    rows = soup.find_all('tr')
    header_rows = [tr for tr in rows if tr.find('th') and not tr.find('td')]
    data_rows = [tr for tr in rows if tr.find('td')]

    # 把每個標題儲存格展開到它佔據的所有 (列, 欄) 位置
    grid = dict()
    for r, tr in enumerate(header_rows):
        c = 0
        for th in tr.find_all('th'):
            while (r, c) in grid:
                c += 1
            rowspan = int(th.get('rowspan', 1))
            colspan = int(th.get('colspan', 1))
            for dr in range(rowspan):
                for dc in range(colspan):
                    grid[(r + dr, c + dc)] = th.get_text(strip=True)
            c += colspan

    names = list()
    if grid:
        for c in range(max(col for _, col in grid) + 1):
            parts = list()
            for r in range(len(header_rows)):
                text = grid.get((r, c))
                if text and (not parts or parts[-1] != text):
                    parts.append(text)
            names.append('/'.join(parts))

    return [dict(zip(names, [td.get_text(strip=True) for td in tr.find_all('td')])) for tr in data_rows]
