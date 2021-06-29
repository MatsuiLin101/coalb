from .configs import *


class CropCostBuilder(object):
    '''
    from apps.coa.builders.cropcost import *
    a = CropCostBuilder()
    '''
    def __init__(self):
        self.driver = None
        self.url = "https://agrstat.coa.gov.tw/sdweb/public/inquiry/InquireAdvance.aspx"
        self.text_title = "農畜產品生產成本統計"
        self.text_group1 = "農產品每公頃生產費用：每公頃生產費用×生產費用與收益_農產品項目"
        self.text_group2 = "農產品每公頃生產量與收益：每公頃生產量與收益×生產費用與收益_農產品項目"
        self.text_group3 = "農產品每公頃人工時數(小時)：人工時數×生產費用與收益_農產品項目"
        self.id_group = "ctl00_cphMain_uctlInquireAdvance_lstFieldGroup"
        self.id_category = "ctl00_cphMain_uctlInquireAdvance_dtlDimension_ctl00_lstDimension"
        self.id_product = "ctl00_cphMain_uctlInquireAdvance_dtlDimension_ctl02_lstDimension"

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
        for option in options:
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

            print(f"Create {parent} {text_group} product {level} {name} {value} {search_name}")
            obj = CropCost.objects.create(
                parent = parent,
                main_class = text_group,
                sub_class = "product",
                level = level,
                name = name,
                value = value,
                search_name = search_name
            )

            if parent is None:
                parent = obj
