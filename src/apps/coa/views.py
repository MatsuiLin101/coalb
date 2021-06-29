from django.shortcuts import render

from apps.coa.apis import *
from apps.coa.utils import (
    pre_process_text_2,
    query_produce_value,
    query_produce_value_product,
)


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
    elif command in ["產量", "種植面積"]:
        api = CropProduceApiView(command, year, city, city_product)
        response = api.api()
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
    return reply
