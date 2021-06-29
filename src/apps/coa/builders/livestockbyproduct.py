from .configs import *


class LivestockByproductBuilder(object):
    '''
    from apps.coa.builders.livestockbyproduct import *
    a = LivestockByproductBuilder()
    '''
    def __init__(self):
        self.driver = None
        self.url = "https://agrstat.coa.gov.tw/sdweb/public/inquiry/InquireAdvance.aspx"
        self.text_title = "畜禽產品生產量值統計"
        self.text_group1 = "畜禽副產品產量"
        self.text_group2 = "蜂蠶飼養產量"
        self.id_group = "ctl00_cphMain_uctlInquireAdvance_lstFieldGroup"
        self.id_city = "ctl00_cphMain_uctlInquireAdvance_dtlDimension_ctl00_lstDimension"
        self.id_product = "ctl00_cphMain_uctlInquireAdvance_dtlDimension_ctl02_lstDimension"

    def build(self):
        LivestockByproduct.objects.all().delete()
        self.driver = get_driver()
        self.driver.get(self.url)
        # 進入畜禽產品生產量值統計頁面
        self.driver.find_element(By.LINK_TEXT, self.text_title).click()
        self.build_city(self.text_group1)
        self.build_product(self.text_group1)
        self.build_city(self.text_group2)
        self.build_product(self.text_group2)
        self.driver.close()

    def build_city(self, text_group):
        # 選擇主分類
        driver_select(self.driver, self.id_group, "text", text_group)
        # 取得次分類城市
        time.sleep(1)
        group_city = self.driver.find_element(By.ID, self.id_city)
        options = group_city.find_elements_by_tag_name("option")
        parent = None
        for option in options:
            value = option.get_attribute("value")
            name = option.text
            level = int(value.split('\t')[-1])
            search_name = name

            if parent is not None:
                if level - parent.level != 1:
                    parent = LivestockByproduct.objects.filter(main_class=text_group, sub_class="city", level=level-1).last()

                origin_parent = parent
                while parent.level > 1:
                    search_name = parent.name + search_name
                    parent = parent.parent
                parent = origin_parent

            print(f"Create {parent} {text_group} city {level} {name} {value} {search_name}")
            obj = LivestockByproduct.objects.create(
                parent = parent,
                main_class = text_group,
                sub_class = "city",
                level = level,
                name = name,
                value = value,
                search_name = search_name
            )

            if parent is None:
                parent = obj

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
                    parent = LivestockByproduct.objects.filter(main_class=text_group, sub_class="product", level=level-1).last()

                origin_parent = parent
                while True:
                    search_name = parent.name + search_name
                    if parent.parent is None:
                        break
                    else:
                        parent = parent.parent
                parent = origin_parent

            print(f"Create {parent} {text_group} product {level} {name} {value} {search_name}")
            obj = LivestockByproduct.objects.create(
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
