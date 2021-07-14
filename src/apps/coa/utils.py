import datetime
import time
import json
import os
import re
import requests
import subprocess
import traceback

from bs4 import BeautifulSoup as bs
from decimal import Decimal
from openpyxl import load_workbook
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import TimeoutException

from django.conf import settings

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
    """
    chrome = settings.CHROME_PATH
    chrome_options = Options()
    if headless:
        chrome_options.add_argument('--headless')
    if use_proxy:
        if new_proxy:
            chrome_options.add_argument(f'--proxy-server={new_proxy}')
        else:
            try:
                obj = CustomSetting.objects.get(name='proxy')
            except Exception as e:
                raise CustomError('請通知管理員設定代理再使用此指令')
            chrome_options.add_argument(f'--proxy-server={obj.value}')
        chrome_options.add_argument('--ignore-ssl-errors=yes')
        chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_argument('User-Agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.70 Safari/537.36"')
    driver = webdriver.Chrome(executable_path=chrome, options=chrome_options)
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
    if method == "value":
        select.select_by_value(target)
    elif method == "text":
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
    if method == "value":
        select.select_by_value(target)
    elif method == "text":
        select.select_by_visible_text(target)
