from .configs import *


class TotalValueBuilder(object):
    '''
    from apps.coa.builders.producevalue import *
    a = TotalValueBuilder()
    '''
    def __init__(self):
        self.driver = None
        self.url = "https://agrstat.moa.gov.tw/sdweb/public/inquiry/InquireAdvance.aspx"
        self.text_title = "農業產值結構與指標"
        self.text_group = "農業產值：縣市別×農業別"
        self.id_group = "ctl00_cphMain_uctlInquireAdvance_lstFieldGroup"
        self.id_city = "ctl00_cphMain_uctlInquireAdvance_dtlDimension_ctl00_lstDimension"
        self.id_category = "ctl00_cphMain_uctlInquireAdvance_dtlDimension_ctl02_lstDimension"

    def build(self):
        TotalValue.objects.all().delete()
        self.driver = get_driver()
        self.driver.get(self.url)
        # 進入農業產值結構與指標頁面
        self.driver.find_element(By.LINK_TEXT, self.text_title).click()
        self.build_city(self.text_group)
        self.build_category(self.text_group)
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
                    parent = TotalValue.objects.filter(main_class=text_group, sub_class="city", level=level-1).last()

                origin_parent = parent
                while parent.level > 1:
                    search_name = parent.name + search_name
                    parent = parent.parent
                parent = origin_parent

            print(f"Create {parent} {text_group} city {level} {name} {value} {search_name}")
            obj = TotalValue.objects.create(
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

    def build_category(self, text_group):
        # 取得次分類產品
        time.sleep(1)
        group_category = self.driver.find_element(By.ID, self.id_category)
        options = group_category.find_elements_by_tag_name("option")
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
                    parent = TotalValue.objects.filter(main_class=text_group, sub_class="category", level=level-1).last()

                origin_parent = parent
                while True:
                    search_name = parent.name + search_name
                    if parent.parent is None:
                        break
                    else:
                        parent = parent.parent
                parent = origin_parent

            print(f"Create {parent} {text_group} category {level} {name} {value} {search_name}")
            obj = TotalValue.objects.create(
                parent = parent,
                main_class = text_group,
                sub_class = "category",
                level = level,
                name = name,
                value = value,
                search_name = search_name
            )

            if parent is None:
                parent = obj
