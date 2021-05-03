from django.shortcuts import render

from apps.coa.apis.value import (
ValueApiView,
)
from apps.coa.apis.gross import (
GrossApiView,
)
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
        command, year, city, city_product = text_list
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
    elif '產地' in text or '批發' in text or '零售' in text:
        reply = parser_product(text)
    elif command == "農家所得" or command == "農牧戶" or command == "耕地面積":
        response = pre_process_text_2(command, year)
        reply = f"{text}\n{response}"
        # if reply is False:
        #     reply = '請輸入年+空格+關鍵字\n例如：\n107 產值 總產值\n107 產值 豬\n107 農家所得\n107 農牧戶\n107 耕地面積'
    elif "指令" in text:
        reply = f"目前提供的指令如下(括號內請改成要查詢的內容，並將底線以空白一格替換)：\n"
        reply += "總產值_(年份)\n"
        reply += "總產值_(年份)_(城市)\n"
        reply += "產值_(年份)_(農產品/畜產品)\n"
        # reply += "產值_(年份)_(城市)_(農產品/畜產品)\n"
        reply += "農家所得_(年份)\n"
        reply += "農牧戶_(年份)\n"
        reply += "耕地面積_(年份)\n"
    else:
        reply = f"很抱歉，您輸入的指令「{text}」可能有誤，無法為您查詢，目前可使用的查詢指令如下(括號內請改成要查詢的內容，並將底線以空白一格替換)：\n"
        reply += "總產值_(年份)\n"
        reply += "總產值_(年份)_(城市)\n"
        reply += "產值_(年份)_(農產品/畜產品)\n"
        # reply += "產值_(年份)_(城市)_(農產品/畜產品)\n"
        reply += "農家所得_(年份)\n"
        reply += "農牧戶_(年份)\n"
        reply += "耕地面積_(年份)\n"
    return reply
