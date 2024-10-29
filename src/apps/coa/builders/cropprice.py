from .configs import *


class CropPriceOriginBuilder(object):
    '''
from apps.coa.builders.cropprice import *
a = CropPriceOriginBuilder()
    '''
    def __init__(self):
        self.driver = None
        self.url = "https://apis.afa.gov.tw/pagepub/AppContentPage.aspx?itemNo=PRI105"
        self.id_category = "WR1_1_Q_GroupCode_XX_C1"
        self.id_table = "WR1_1_PRMG_0_X"
        self.css_query = "div.CSS_ABS_Normal"

    def build(self, use_proxy=False):
        if use_proxy:
            return self._build()
        else:
            res = requests.get(f"{settings.PROXY_DOMAIN}{reverse('coa:proxy_build')}?token={settings.PROXY_TOKEN}&api=CropPriceOriginBuilder")
            data = json.loads(res.text)
            CropPriceOrigin.objects.all().delete()
            for item in data:
                obj = CropPriceOrigin.objects.create(**item)
                print(f'create {obj.category} {obj}')

    def _build(self):
        self.driver = get_driver()
        self.driver.get(self.url)
        # 進入農糧署農產品產地價格查報系統
        select_category = self.driver.find_element(By.ID, self.id_category)
        options = select_category.find_elements(By.TAG_NAME, "option")
        count_option = 0
        count_table = 0
        data = list()
        while count_option < len(options):
            select_category = self.driver.find_element(By.ID, self.id_category)
            option = select_category.find_elements(By.TAG_NAME, "option")[count_option]
            count_option += 1
            count_table += 1
            category = option.text
            id_table = self.id_table.replace('_X', f'{count_table}')
            driver_select(self.driver, self.id_category, "text", category)
            WebDriverWait(self.driver, 30, 0.1).until(EC.presence_of_element_located((By.ID, id_table)))

            table = self.driver.find_element(By.ID, id_table)
            query = self.driver.find_element(By.CSS_SELECTOR, self.css_query)
            id_query = query.get_attribute('id')
            tds = table.find_elements(By.TAG_NAME, 'td')
            for td in tds:
                name = td.text
                if len(name) == 0:
                    continue
                input = td.find_element(By.TAG_NAME, 'input')
                value = input.get_attribute('value')
                code = input.get_attribute('id')
                data.append({
                    'category': category,
                    'id_table': id_table,
                    'id_query': id_query,
                    'value': value,
                    'code': code,
                    'name': name
                })
        self.driver.close()
        return data

    def close(self):
        self.driver.close()


class CropPriceWholesaleBuilder(object):
    '''
from apps.coa.builders.cropprice import *
a = CropPriceWholesaleBuilder()
    '''
    def __init__(self):
        self.driver = None
        self.url = "https://agrstat.moa.gov.tw/sdweb/public/inquiry/InquireAdvance.aspx"
        self.text_title = "農產品價格統計"
        self.text_group1 = "蔬菜批發價格：蔬菜別"
        self.text_group2 = "果品批發價格：果品別"
        self.text_group3 = "白米批發(躉售)價格：稻種別"
        self.id_group = "ctl00_cphMain_uctlInquireAdvance_lstFieldGroup"
        self.id_product = "ctl00_cphMain_uctlInquireAdvance_dtlDimension_ctl00_lstDimension"

    def build(self):
        CropPriceWholesale.objects.all().delete()
        self.driver = get_driver()
        self.driver.get(self.url)
        # 進入農產品價格統計頁面
        self.driver.find_element(By.LINK_TEXT, self.text_title).click()
        self.build_city(self.text_group1)
        self.build_city(self.text_group2)
        self.build_city(self.text_group3)
        self.driver.close()

    def build_city(self, text_group):
        # 選擇主分類
        driver_select(self.driver, self.id_group, "text", text_group)
        # 取得次分類產品批發類別
        time.sleep(1)
        group_product = self.driver.find_element(By.ID, self.id_product)
        options = group_product.find_elements_by_tag_name("option")
        parent = None
        for option in options:
            value = option.get_attribute("value")
            name = option.text
            level = int(value.split('\t')[-1])
            search_name = name

            # if parent is not None:
            #     if level - parent.level != 1:
            #         parent = CropPriceWholesale.objects.filter(main_class=text_group, sub_class="city", level=level-1).last()
            #
            #     origin_parent = parent
            #     while parent.level > 1:
            #         search_name = parent.name + search_name
            #         parent = parent.parent
            #     parent = origin_parent

            print(f"Create {parent} {text_group} city {level} {name} {value} {search_name}")
            obj = CropPriceWholesale.objects.create(
                parent = parent,
                main_class = text_group,
                sub_class = "product",
                level = level,
                name = name,
                value = value,
                search_name = search_name
            )

            # if parent is None:
            #     parent = obj
