from .configs import *


class CropCostBuilder(object):
    '''
    from apps.coa.builders.cropcost import *
    a = CropCostBuilder()
    '''
    def __init__(self):
        self.driver = None
        self.url = "https://agrstat.moa.gov.tw/sdweb/public/inquiry/InquireAdvance.aspx"
        self.text_title = "農畜產品生產成本統計"
        self.text_group1 = "農產品每公頃生產費用：每公頃生產費用×生產費用與收益_農產品項目"
        self.text_group2 = "農產品每公頃生產量與收益：每公頃生產量與收益×生產費用與收益_農產品項目"
        self.text_group3 = "農產品每公頃人工時數(小時)：人工時數×生產費用與收益_農產品項目"
        self.id_group = "ctl00_cphMain_uctlInquireAdvance_lstFieldGroup"
        self.id_category = "ctl00_cphMain_uctlInquireAdvance_dtlDimension_ctl00_lstDimension"
        self.id_product = "ctl00_cphMain_uctlInquireAdvance_dtlDimension_ctl02_lstDimension"
        self.id_query = "ctl00_cphMain_uctlInquireAdvance_btnQuery"
        self.id_back = "ctl00_cphMain_uctlInquireAdvance_btnBack2"
        self.id_start_year = "ctl00_cphMain_uctlInquireAdvance_ddlYearBegin"
        self.id_end_year = "ctl00_cphMain_uctlInquireAdvance_ddlYearEnd"

    def build(self):
        CropCost.objects.all().delete()
        self.driver = get_driver()
        self.driver.get(self.url)
        # 進入農畜產品生產成本統計頁面
        self.driver.find_element(By.LINK_TEXT, self.text_title).click()
        self.build_category(self.text_group1)
        self.build_product(self.text_group1)
        self.build_category(self.text_group2)
        self.build_product(self.text_group2)
        self.build_category(self.text_group3)
        self.build_product(self.text_group3)
        self.driver.close()

    def build_category(self, text_group):
        # 選擇主分類
        driver_select(self.driver, self.id_group, "text", text_group)
        # 取得次分類類別
        time.sleep(1)
        group_category = self.driver.find_element(By.ID, self.id_category)
        options = group_category.find_elements_by_tag_name("option")
        parent = None
        for option in options:
            if '生產費用總計' not in option.text and '粗收益' not in option.text and '男工' not in option.text and '女工' not in option.text:
                continue
            value = option.get_attribute("value")
            name = option.text
            level = int(value.split('\t')[-1])
            search_name = name

            print(f"Create {parent} {text_group} category {level} {name} {value} {search_name}")
            obj = CropCost.objects.create(
                parent = parent,
                main_class = text_group,
                sub_class = "category",
                level = level,
                name = name,
                value = value,
                search_name = search_name
            )

    def build_product(self, text_group):
        # 取得次分類產品
        time.sleep(1)
        group_product = self.driver.find_element(By.ID, self.id_product)
        options = group_product.find_elements_by_tag_name("option")
        parent = None
        index = 0
        while index < len(options):
            group_product = self.driver.find_element(By.ID, self.id_product)
            options = group_product.find_elements_by_tag_name("option")
            option = options[index]
            value = option.get_attribute("value")
            name = option.text
            level = int(value.split('\t')[-1])
            search_name = name

            if level == 1:
                parent = None

            if parent is not None:
                if level - parent.level != 1:
                    parent = CropCost.objects.filter(main_class=text_group, sub_class="product", level=level-1).last()

                origin_parent = parent
                while True:
                    search_name = parent.name + search_name
                    if parent.parent is None:
                        break
                    else:
                        parent = parent.parent
                parent = origin_parent

            # 取得作物資料起始到結束年份
            driver_select(self.driver, self.id_product, "text", name, cancel=True)
            # time.sleep(1)
            self.driver.find_element(By.ID, self.id_query).click()
            # time.sleep(1)
            start_year_list = list()
            start_year = self.driver.find_element(By.ID, self.id_start_year)
            start_year_options = start_year.find_elements_by_tag_name('option')
            for opt in start_year_options:
                year = int(opt.get_attribute('value'))
                start_year_list.append(year)
            start_year = min(start_year_list)

            end_year_list = list()
            end_year = self.driver.find_element(By.ID, self.id_end_year)
            end_year_options = end_year.find_elements_by_tag_name('option')
            for opt in end_year_options:
                year = int(opt.get_attribute('value'))
                end_year_list.append(year)
            end_year = max(end_year_list)

            self.driver.find_element(By.ID, self.id_back).click()
            # time.sleep(1)
            index += 1

            print(f"Create {parent} {text_group} product {level} {name} {value} {search_name} {start_year} {end_year}")
            obj = CropCost.objects.create(
                parent = parent,
                main_class = text_group,
                sub_class = "product",
                level = level,
                name = name,
                value = value,
                search_name = search_name,
                start_year = start_year,
                end_year = end_year,
            )

            if parent is None:
                parent = obj
