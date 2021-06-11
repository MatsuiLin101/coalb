from .configs import *


class LivestockPriceApiView(ApiView):
    '''
    其他畜禽價格api介面
    -拍賣價
    -產地價
    -零售價
    畜產品價格查詢系統 http://price.naif.org.tw/Query/Query_now.aspx
    '''
    def __init__(self, command, query_date, product):
        self.command = command
        self.query_date = query_date
        self.product = product

    def chose_api(self):
        if command == "拍賣價":
            return Sale(query_date, product)

    def api(self):
        try:
            self.check_year()
            if not self.message:
                self.get_data()
        except Exception as e:
            if not self.message:
                self.message = f"搜尋「{self.command} {self.product} {self.query_date}」發生錯誤"
        if self.driver:
            self.driver.close()
        return self.message

    def check_year(self):
        # check years
        # 檢查年份是否為數字
        try:
            int(self.selfyear)
        except Exception as e:
            self.message = f"年份「{self.selfyear}」無效，請輸入民國年"
            return
        # 檢查月份是否為數字
        if self.selfmonth:
            try:
                int(self.selfmonth)
            except Exception as e:
                self.message = f"月份「{self.selfmonth}」無效，請輸入1～12"
                return
        self.select_value = f"{self.selfyear.zfill(3)}{self.selfmonth.zfill(2)}" if self.selfmonth else f"{self.selfyear.zfill(3)}"


class Sale(LivestockPriceApiView):
    '''
    拍賣價api介面
    '''
    def __init__(self, query_date, product):
        self.driver = None
        self.url = "https://agrstat.coa.gov.tw/sdweb/public/inquiry/InquireAdvance.aspx"
        self.check_box = "ContentPlaceHolder_content_uc_productList_mixVer_CheckBoxList_priceType_1"
        self.btn_query = "ctl00$ContentPlaceHolder_content$Button_query"
        self.table_option = "ContentPlaceHolder_content_uc_productList_mixVer_Panel_data"
        self.table_result = "ContentPlaceHolder_content_GridView_data"
        self.query_date = query_date
        self.product = product

    def get_data(self):
        driver = get_driver()
        driver.get(self.url)
        check_box = driver.find_element(By.ID, self.check_box)
        check_box.click()



driver = get_driver(False)
driver.get(url)

id_list = [
    'ContentPlaceHolder_content_uc_productList_mixVer_CheckBoxList_priceType_0',
    'ContentPlaceHolder_content_uc_productList_mixVer_CheckBoxList_priceType_1',
    'ContentPlaceHolder_content_uc_productList_mixVer_CheckBoxList_priceType_2'
]

for id in id_list:
    check_box = driver.find_element(By.ID, id)
    check_box.click()
    id_table = 'ContentPlaceHolder_content_uc_productList_mixVer_Panel_data'
    table = driver.find_element(By.ID, id_table)
    labels = table.find_elements(By.TAG_NAME, 'label')
    for label in labels:
        print(label.text)
    check_box = driver.find_element(By.ID, id)
    check_box.click()
    print('-----------')

id1 = 'ContentPlaceHolder_content_uc_productList_mixVer_CheckBoxList_priceType_0'
check_box = driver.find_element(By.ID, id1)
check_box.click()

id_table = 'ContentPlaceHolder_content_uc_productList_mixVer_Panel_data'
target_list = list()
table = driver.find_element(By.ID, id_table)
tds = table.find_elements(By.TAG_NAME, 'td')
for td in tds:
    try:
        label = td.find_element(By.TAG_NAME, 'label')
        if '豬' in label.text:
            target_list.append(label.text)
    except Exception as e:
        continue

table = driver.find_element(By.ID, id_table)
for target in target_list:
    check_target = None
    tds = table.find_elements(By.TAG_NAME, 'td')
    for td in tds:
        try:
            label = td.find_element(By.TAG_NAME, 'label')
            if label.text == target:
                check_target = td.find_element(By.TAG_NAME, 'input')
                break
        except Exception as e:
            continue
    if check_target:
        check_target.click()


a = tds[2]
b = a.find_element(By.TAG_NAME, 'label')

for label in labels:
    print(label.text)

check_box.click()

id2 = 'ContentPlaceHolder_content_uc_productList_mixVer_CheckBoxList_priceType_1'

id3 = 'ContentPlaceHolder_content_uc_productList_mixVer_CheckBoxList_priceType_2'
