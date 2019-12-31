import requests

from collections import deque

from bs4 import BeautifulSoup as bs

from .models import SD

URL = "https://agrstat.coa.gov.tw/sdweb/public/inquiry/InquireAdvance.aspx"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36",
}
KEY_LIST = [
    "__EVENTTARGET",
    "__EVENTARGUMENT",
    "__LASTFOCUS",
    "__VIEWSTATE",
    "__VIEWSTATEGENERATOR",
    "__EVENTVALIDATION",
]


def get_viewset():
    print('6')
    res = requests.get(URL, headers=HEADERS, verify=False)
    return bs(res.text)


def get_formdata(value):
    print('5')
    soup = get_viewset()
    viewstate = soup.find_all("input", {"id": "__VIEWSTATE"})[0].get("value")
    viewstategenerator = soup.find_all("input", {"id": "__VIEWSTATEGENERATOR"})[0].get("value")
    eventvalidation = soup.find_all("input", {"id": "__EVENTVALIDATION"})[0].get("value")

    data = {
        "__EVENTTARGET": value,
        "__EVENTARGUMENT": "",
        "__VIEWSTATE": viewstate,
        "__VIEWSTATEGENERATOR": viewstategenerator,
        "__EVENTVALIDATION": eventvalidation,
        "ctl00$cphMain$uctlInquireAdvance$txtQGrouptName": "",
    }
    return data


def get_formdata_detail(parent_value, value):
    print('4')
    data = get_formdata(parent_value)
    soup = post_formdata(data)
    viewstate = soup.find_all("input", {"id": "__VIEWSTATE"})[0].get("value")
    viewstategenerator = soup.find_all("input", {"id": "__VIEWSTATEGENERATOR"})[0].get("value")
    eventvalidation = soup.find_all("input", {"id": "__EVENTVALIDATION"})[0].get("value")

    data = {
        "ctl00$cphMain$uctlInquireAdvance$ScriptManager1": "ctl00$cphMain$uctlInquireAdvance$UpdatePanel2|ctl00$cphMain$uctlInquireAdvance$lstFieldGroup",
        "ctl00$cphMain$uctlInquireAdvance$lstFieldGroup": value,
        "__EVENTTARGET": "ctl00$cphMain$uctlInquireAdvance$lstFieldGroup",
        "__EVENTARGUMENT": "",
        "__LASTFOCUS": "",
        "__VIEWSTATE": viewstate,
        "__VIEWSTATEGENERATOR": viewstategenerator,
        "__EVENTVALIDATION": eventvalidation,
        "__ASYNCPOST": "true",
    }
    return data


def get_formdata_to_query(text):
    print('3')
    text = text.split(" ")
    print(f'text {text}')
    product = text[0]
    print(f'product {product}')
    type = text[1]
    print(f'type {type}')
    obj = SD.objects.filter(name__icontains=product, parent__name__icontains=type).first()
    print(f'obj {obj}')
    db = obj.parent.parent
    print(f'db {db}')
    type = obj.parent
    print(f"type {type}")
    data = get_formdata_detail(db.value, type.value)
    soup = post_formdata(data)
    s = soup.findAll(text=True)[-1].replace("\r\n", "").replace(" ", "")
    s = s.split("|")
    que = deque(s)
    while len(que) > 0:
        key = que.popleft()
        if key in KEY_LIST:
            data[key] = que.popleft()
    data.update({
        "ctl00$cphMain$uctlInquireAdvance$btnQuery": "查詢確認",
        "ctl00$cphMain$uctlInquireAdvance$lstFieldGroup": type.value,
        "ctl00$cphMain$uctlInquireAdvance$dtlDimension$ctl00$lstDimension": obj.value,
    })
    return obj, data


def post_formdata(data):
    print('7')
    res = requests.post(URL, data=data, headers=HEADERS, verify=False)
    return bs(res.text)


def post_to_query(text):
    print('2')
    obj, data = get_formdata_to_query(text)
    res = requests.post(URL, data=data, headers=HEADERS, verify=False)
    return obj, bs(res.text)


def parser_product(text):
    year = str()
    month = str()
    price = str()
    print('1')
    obj, soup = post_to_query(text)

    for i in soup.find_all("td", {"class": "VerDim"}):
        if "年" in i.text:
            year = i.text
        if "月" in i.text:
            month = i.text

    for i in soup.find_all("td", {"class": "ValueLeft"}):
        price = i.text

    if obj is None:
        return f"{text} 找不到結果"
    else:
        result = f"搜尋 {text} 的結果為：\n{obj.name}\n{year} - {month} - {price}"
    print(result)
    return result


def parser_sd():
    soup = get_viewset()
    target = soup.find_all("a", {"style": "white-space:nowrap;"})
    for t in target:
        name = t.text
        if name == '農產品價格統計':
            value = t.get("href").split("'")[1]
            SD.objects.create(name=name, value=value)


def parser_lay1():
    sd = SD.objects.filter(parent=None)

    for i in sd:
        data = get_formdata1(i.value)
        soup = post_formdata(data)
        for option in soup.find("select", {"name": "ctl00$cphMain$uctlInquireAdvance$lstFieldGroup"}).find_all("option"):
            name = option.text
            value = option.get("value")
            SD.objects.create(name=name, value=value, layer=1, parent=i)


def parser_lay2():
    sd = SD.objects.filter(parent=None)

    for parent in sd:
        for lay1 in parent.sd_set.all():
            data = get_formdata2(parent.value, lay1.value)
            print(f"post {parent.name} - {parent.value} : {lay1.name} - {lay1.value}")
            soup = post_formdata(data)
            try:
                lay2 = soup.find_all("select", {"name": "ctl00$cphMain$uctlInquireAdvance$dtlDimension$ctl00$lstDimension"})
                if lay2:
                    for option in lay2[0].find_all("option"):
                        name = option.text
                        value = option.get("value")
                        SD.objects.create(name=name, value=value, layer=2, parent=lay1)

                lay3 = soup.find_all("select", {"name": "ctl00$cphMain$uctlInquireAdvance$dtlDimension$ctl02$lstDimension"})
                if lay3:
                    for option in lay3[0].find_all("option"):
                        name = option.text
                        value = option.get("value")
                        SD.objects.create(name=name, value=value, layer=3, parent=lay1)

                lay4 = soup.find_all("select", {"name": "ctl00$cphMain$uctlInquireAdvance$dtlDimension$ctl04$lstDimension"})
                if lay4:
                    for option in lay4[0].find_all("option"):
                        name = option.text
                        value = option.get("value")
                        SD.objects.create(name=name, value=value, layer=4, parent=lay1)

            except Exception as e:
                print(f"Error {parent.name}, {lay1.name}, {name}, {value}")