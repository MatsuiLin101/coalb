from openpyxl import load_workbook

from django.shortcuts import render

from apps.coa.apis import *
from apps.coa.utils import (
    pre_process_text_2,
    query_produce_value,
    query_produce_value_product,
)
from apps.coa.models import ProductCode, CropProduceUnit


def api_view(text):
    # 將輸入的文字依據空格分割
    text_list = text.split(' ')
    if len(text_list) == 2:
        command, year = text_list
        city_product = None
        product = None
    elif len(text_list) == 3:
        command, year, city_product = text_list
        city = None
    elif len(text_list) == 4:
        command, year, city_product, city = text_list
    else:
        command = None
        year = None
        city = None
        city_product = None

    # 判斷分割後的第一組文字是哪一個指令
    if command == "總產值":
        response = query_produce_value(year, city_product)
        reply = f"{text}\n{response}"
    elif command == "產值":
        api = ValueApiView(year, city_product)
        response = api.api()
        reply = f"{text}\n{response}"
    elif command == "生產毛額":
        api = GrossApiView(year)
        response = api.api()
        reply = f"{text}\n{response}"
    elif command == "農家所得":
        api = IncomeApiView(year)
        response = api.api()
        reply = f"{text}\n{response}"
    elif command  == "農牧戶":
        api = FarmerApiView(year)
        response = api.api()
        reply = f"{text}\n{response}"
    elif command == "耕地面積":
        api = FarmerAreaApiView(year)
        response = api.api()
        reply = f"{text}\n{response}"
    elif command == "災害":
        api = DisasterApiView(year)
        response = api.api()
        reply = f"{text}\n{response}"
    elif command == "就業人口":
        api = LaborforceApiView(year)
        response = api.api()
        reply = f"{text}\n{response}"
    elif command in ["農保", "老農津貼", "獎助學金"]:
        api = WelfareApiView(command, year, city_product)
        response = api.chose_api().api()
        reply = f"{text}\n{response}"
    elif command in ["產地", "批發"]:
        api = CropPriceApiView(command, year, city_product, city)
        response = api.choice_api().api()
        reply = f"{text}\n{response}"
    elif command in ["產量", "種植面積", "單位產值", "單位產量"]:
        api = CropProduceApiView(command, year, city, city_product)
        response = api.api()
        reply = f"{text}\n{response}"
    elif command in ["單位產值", "單位產量"]:
        api = CropProduceApiView(command, year, city, city_product)
        response = api.api()
        reply = f"{text}\n{response}"
    elif command in ["生產成本", "生產費用", "粗收益", "淨收入率", "工時"]:
        api = CropCostApiView(command, year, city_product)
        response = api.chose_api().api()
        reply = f"{text}\n{response}"
    elif command in ["交易量", "價格", "重量"]:
        api = LivestockHogApiView(command, year)
        response = api.api()
        reply = f"{text}\n{response}"
    elif command in ["拍賣價", "產地價", "零售價"]:
        api = LivestockPriceApiView(command, year, city_product)
        response = api.chose_api().api()
        reply = f"{text}\n{response}"
    elif command in ["場數"]:
        api = LivestockFeedlotApiView(year, city_product, city)
        response = api.api()
        reply = f"{text}\n{response}"
    elif command in ["在養量"]:
        api = LivestockFeedamountApiView(year, city_product, city)
        response = api.api()
        reply = f"{text}\n{response}"
    elif command in ["屠宰"]:
        api = LivestockSlaughterApiView(year, city_product, city)
        response = api.api()
        reply = f"{text}\n{response}"
    elif command in ["副產", "副產品", "副產物"]:
        api = LivestockByproductApiView(year, city_product, city)
        response = api.api()
        reply = f"{text}\n{response}"
    elif command in ["代碼"]:
        api = ProductCodeApiView(year)
        response = api.api()
        reply = f"{text}\n{response}"
    elif '產地' in text or '批發' in text or '零售' in text:
        reply = parser_product(text)
        # if reply is False:
        #     reply = '請輸入年+空格+關鍵字\n例如：\n107 產值 總產值\n107 產值 豬\n107 農家所得\n107 農牧戶\n107 耕地面積'
    elif "指令" in text:
        reply = f"目前提供的指令如下(括號內請改成要查詢的內容，並將底線以空白一格替換)：\n"
        reply += "總產值_(年份)\n"
        reply += "總產值_(年份)_(城市)\n"
        reply += "產值_(年份)_(農產品/畜產品)\n"
        # reply += "產值_(年份)_(城市)_(農產品/畜產品)\n"
        reply += "生產毛額_(年份)\n"
        reply += "農家所得_(年份)\n"
        reply += "農牧戶_(年份)\n"
        reply += "耕地面積_(年份)\n"
        reply += "災害_(年份)\n"
        reply += "就業人口_(年份)\n就業人口_(年份)/(月份)\n"
        reply += "老農津貼_(年份)/(月份)\n農保_(年份)/(月份)_(城市)\n"
        reply += "獎助學金_(年份)\n"
        reply += "產量_(年份)_(縣市鄉鎮)_(作物)\n"
        reply += "種植面積_(年份)_(縣市鄉鎮)_(作物)\n"
        reply += "生產成本_(年份)_(作物)\n"
        reply += "生產費用_(年份)_(作物)\n"
        reply += "粗收益_(年份)_(作物)\n"
        reply += "淨收入率_(年份)_(作物)\n"
        reply += "工時_(年份)_(作物)\n"
        reply += "交易量_(年份)_豬\n"
        reply += "價格_(年份)_豬\n"
        reply += "重量_(年份)_豬\n"
        reply += "拍賣價_(年份)_(畜禽)\n"
        reply += "產地價_(年份)_(畜禽)\n"
        reply += "零售價_(年份)_(畜禽)\n"
        reply += "場數_(年份)_(畜禽)_(城市)\n"
        reply += "在養量_(年份)_(畜禽)_(城市)\n"
        reply += "屠宰_(年份)_(畜禽)_(城市)\n"
        reply += "產量_(年份)_(畜禽)_(城市)\n"
        reply += "代碼_(作物)\n"
    else:
        reply = f"很抱歉，您輸入的指令「{text}」可能有誤，無法為您查詢，目前可使用的查詢指令如下(括號內請改成要查詢的內容，並將底線以空白一格替換)：\n"
        reply += "總產值_(年份)\n"
        reply += "總產值_(年份)_(城市)\n"
        reply += "產值_(年份)_(農產品/畜產品)\n"
        # reply += "產值_(年份)_(城市)_(農產品/畜產品)\n"
        reply += "生產毛額_(年份)\n"
        reply += "農家所得_(年份)\n"
        reply += "農牧戶_(年份)\n"
        reply += "耕地面積_(年份)\n"
        reply += "災害_(年份)\n"
        reply += "就業人口_(年份)\n就業人口_(年份)/(月份)\n"
        reply += "老農津貼_(年份)/(月份)\n農保_(年份)/(月份)_(城市)\n"
        reply += "獎助學金_(年份)\n"
        reply += "產量_(年份)_(縣市鄉鎮)_(作物)\n"
        reply += "種植面積_(年份)_(縣市鄉鎮)_(作物)\n"
        reply += "生產成本_(年份)_(作物)\n"
        reply += "生產費用_(年份)_(作物)\n"
        reply += "粗收益_(年份)_(作物)\n"
        reply += "淨收入率_(年份)_(作物)\n"
        reply += "工時_(年份)_(作物)\n"
        reply += "交易量_(年份)_豬\n"
        reply += "價格_(年份)_豬\n"
        reply += "重量_(年份)_豬\n"
        reply += "拍賣價_(年份)_(畜禽)\n"
        reply += "產地價_(年份)_(畜禽)\n"
        reply += "零售價_(年份)_(畜禽)\n"
        reply += "場數_(年份)_(畜禽)_(城市)\n"
        reply += "在養量_(年份)_(畜禽)_(城市)\n"
        reply += "屠宰_(年份)_(畜禽)_(城市)\n"
        reply += "產量_(年份)_(畜禽)_(城市)\n"
        reply += "代碼_(作物)\n"
    return reply


def file_view_product_code(file_name):
    try:
        ProductCode.objects.all().delete()
        main_count = 0
        labor_count = 0

        wb = load_workbook(file_name)
        ws = wb['主力代碼']
        for row in ws.rows:
            code = row[0]
            name = row[1]
            if code.row <= 1:
                continue
            else:
                obj = ProductCode.objects.create(category='主力', code=code.value, name=name.value)
                main_count += 1

        ws = wb['勞動力代碼']
        for row in ws.rows:
            code = row[0]
            name = row[1]
            if code.row <= 1:
                continue
            else:
                obj = ProductCode.objects.create(category='勞動力', code=code.value, name=name.value)
                labor_count += 1

        return f"上傳主力代碼{main_count}筆，勞動力代碼{labor_count}筆成功！"
    except Exception as e:
        raise


def file_view_crop_produce(file_name):
    CropProduceUnit.objects.all().delete()
    wb = load_workbook(file_name)
    for sheet in wb.sheetnames:
        if "稻" in sheet:
            col_period = "C"
            col_city_district = None
        else:
            col_period = None
            col_city_district = "E"
        col_name = col_city = col_district = col_city_code = col_district_code = None
        col_amount_max = col_amount_min = col_amount_average = col_value_min = col_value_average = None
        amount_unit = value_unit = None

        ws = wb[sheet]
        for cell in ws[1]:
            if cell.value is None:
                continue
            elif "產量" in cell.value and "平均" not in cell.value:
                amount_unit = "(" + cell.value.split("(")[-1]
            elif "產值" in cell.value and "平均" not in cell.value:
                value_unit = "(" + cell.value.split("(")[-1]

        for cell in ws[2]:
            value = cell.value
            letter = cell.column_letter
            if value is None:
                continue
            elif "農產別" in value or "稻種別" in value:
                col_name = letter
            elif "縣市別" in value:
                col_city = letter
            elif "鄉鎮別" in value and col_period:
                col_city = letter
            elif "鄉鎮別" in value:
                col_district = letter
            elif "縣市代碼" in value:
                col_city_code = letter
            elif "鄉鎮代碼" in value:
                col_district_code = letter
            elif "MAX" in value:
                if col_amount_max is None:
                    col_amount_max = letter
                else:
                    col_value_max = letter
            elif "MIN" in value:
                if col_amount_min is None:
                    col_amount_min = letter
                else:
                    col_value_min = letter
            elif "age" in value:
                if col_amount_average is None:
                    col_amount_average = letter
                else:
                    col_value_average = letter

        for index in range(3, ws.max_row + 1):
            display_name = ws[f"A{index}"].value
            name = ws[f"{col_name}{index}"].value
            city = ws[f"{col_city}{index}"].value
            city_code = ws[f"{col_city_code}{index}"].value
            district_code = ws[f"{col_district_code}{index}"].value
            amount_max = ws[f"{col_amount_max}{index}"].value
            amount_min = ws[f"{col_amount_min}{index}"].value
            amount_average = ws[f"{col_amount_average}{index}"].value
            value_max = ws[f"{col_value_max}{index}"].value
            value_min = ws[f"{col_value_min}{index}"].value
            value_average = ws[f"{col_value_average}{index}"].value

            obj = CropProduceUnit.objects.create(
                category = sheet,
                display_name = display_name,
                name = name,
                city = city,
                city_code = city_code,
                district_code = district_code,
                amount_min = amount_min,
                amount_max = amount_max,
                amount_average = amount_average,
                value_min = value_min,
                value_max = value_max,
                value_average = value_average,
            )
            update = False
            if col_period:
                obj.period = ws[f"{col_period}{index}"].value
                update = True
            if col_district:
                obj.district = ws[f"{col_district}{index}"].value
                update = True
            if col_city_district:
                obj.city_district = ws[f"{col_city_district}{index}"].value
                update = True
            if amount_unit:
                obj.amount_unit = amount_unit
                update = True
            if value_unit:
                obj.value_unit = value_unit
                update = True
            if update:
                obj.save()
