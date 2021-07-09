from apps.coa.utils import *


class BasicApiView(object):
    '''
    Basic view for coa apis
    '''
    def __init__(self, params):
        self.params = params
        self.command_text = " ".join(text for text in params)

    @property
    def classname(self):
        return self.__class__.__name__

    def execute_api(self):
        '''
        execute api
        '''
        try:
            self.verify_date()
            self.get_data()
        except CustomError:
            raise
        except Exception as e:
            traceback_log = TracebackLog.objects.create(app=f"{self.classname}", message=traceback.format_exc())
            self.message = f"「{self.command_text}」發生未知錯誤，錯誤編號「{traceback_log.id}」，請通知管理員處理"
        if self.driver:
            self.driver.close()
        return self.message

    def verify_date(self):
        # 檢查年份是否為數字
        try:
            self.year = int(self.query_date)
        except Exception as e:
            self.message = f"年份「{self.query_date}」無效，請輸入民國年"
            raise CustomError(self.message)

    def parser(self):
        self.driver = get_driver()
        self.driver.get(self.url)


class AnnualReportBasicApiView(BasicApiView):
    '''
    年報用公版ApiView
    如果年報持續報錯，或是轉檔失敗，且時間在6~8月左右，可能是年報更新導致抓不到更新的年報
    '''
    def __init__(self, params):
        self.driver = None
        self.url = "https://agrstat.coa.gov.tw/sdweb/public/book/Book.aspx"
        self.radio_history = "ctl00_cphMain_uctlBook_rdoPeriodAll"
        self.btn_total = "ctl00_cphMain_uctlBook_chkQCategoryAll"
        self.btn_book = "ctl00_cphMain_uctlBook_dltQCategory_ctl00_chkQCategory"
        self.btn_search = "ctl00_cphMain_uctlBook_btnQuery"
        self.id_table = "ctl00_cphMain_uctlBook_grdBook"
        self.id_book1 = ""
        self.id_book2 = ""
        self.xlsx_name = ""
        self.message = ""
        self.row = ""
        self.params = params
        self.command_text = " ".join(text for text in params)

    def execute_api(self):
        try:
            self.download()
            self.open_wb()
            self.verify_date()
            self.get_data()
        except CustomError:
            self.driver.close() if self.driver else None
            os.remove(self.xlsx_name) if self.xlsx_name else None
            raise
        except Exception as e:
            traceback_log = TracebackLog.objects.create(app=f"{self.classname}", message=traceback.format_exc())
            self.message = f"「{self.command_text}」發生未知錯誤，錯誤編號「{traceback_log.id}」，請通知管理員處理"
        self.driver.close() if self.driver else None
        os.remove(self.xlsx_name) if self.xlsx_name else None
        return self.message

    def verify_date(self):
        # verify query year
        try:
            self.year = int(self.query_date)
        except Exception as e:
            self.message = f"年份「{self.query_date}」無效，請輸入民國年"
            raise CustomError(self.message)

        list_years = list()
        for row in self.ws.rows:
            year = row[1].value
            if year is not None:
                try:
                    int(year)
                    list_years.append(year)
                except Exception as e:
                    continue

                if str(self.year) == str(year):
                    self.row = row[0].row
                    return
        self.message = f"「{self.command_text}」年份必需在{list_years[0]}~{list_years[-1]}之間"
        raise CustomError(self.message)

    def open_wb(self):
        # open value xslx
        wb = load_workbook(filename=self.xlsx_name)
        self.ws = wb[wb.sheetnames[0]]

    def download(self):
        '''
        避免年報更新時的空窗期，抓取最新一期的年報及前一期的年報，並備註資料來源
        '''
        # download ods and transfer to xlsx
        self.driver = get_driver()
        try:
            self.driver.get(self.url)
            WebDriverWait(self.driver, 30, 0.1).until(EC.presence_of_element_located((By.ID, self.btn_search)))
            self.driver.find_element(By.ID, self.radio_history).click()
            self.driver.find_element(By.ID, self.btn_total).click()
            self.driver.find_element(By.ID, self.btn_book).click()
            self.driver.find_element(By.ID, self.btn_search).click()
            WebDriverWait(self.driver, 30, 0.1).until(EC.presence_of_element_located((By.ID, self.id_table)))
            table = self.driver.find_element(By.ID, self.id_table)
            reports = table.find_elements(By.TAG_NAME, 'a')
            for report in reports:
                if "農業統計年報" in report.text and self.id_book1 == "":
                    self.id_book1 = report.get_attribute("id")
                    self.source1 = report.text
                    continue
                elif "農業統計年報" in report.text and self.id_book2 == "":
                    self.id_book2 = report.get_attribute("id")
                    self.source2 = report.text
                    continue
                elif self.id_book1 and self.id_book2:
                    break

            try:
                self.driver.find_element(By.ID, self.id_book1).click()
                ods = self.driver.find_element(By.ID, self.id_ods)
                self.source = self.source1
            except Exception as e:
                try:
                    self.driver.get(self.url)
                    WebDriverWait(self.driver, 30, 0.1).until(EC.presence_of_element_located((By.ID, self.btn_search)))
                    self.driver.find_element(By.ID, self.radio_history).click()
                    self.driver.find_element(By.ID, self.btn_total).click()
                    self.driver.find_element(By.ID, self.btn_book).click()
                    self.driver.find_element(By.ID, self.btn_search).click()
                    WebDriverWait(self.driver, 30, 0.1).until(EC.presence_of_element_located((By.ID, self.id_book2)))
                    self.driver.find_element(By.ID, self.id_book2).click()
                    ods = self.driver.find_element(By.ID, self.id_ods)
                    self.source = self.source2
                except Exception as e:
                    raise

            ods_href = ods.get_attribute("href")
            ods_name = f"ods_{int(datetime.datetime.now().timestamp())}.ods"
            res = requests.get(ods_href)
            with open(ods_name, 'wb') as f:
                f.write(res.content)
            subprocess.Popen(f'{settings.LIBREOFFICE_PATH} --headless --invisible --convert-to xlsx {ods_name}', shell=True, stderr=subprocess.PIPE).communicate()
            self.xlsx_name = ods_name.replace('.ods', '.xlsx')
            os.remove(ods_name)
        except Exception as e:
            raise
