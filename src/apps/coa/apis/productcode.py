from .configs import *


class ProductCodeApiView(BasicApiView):
    '''
    作物代碼api介面
    (NEW)productcode(作物代碼)
    EXCEL匯入
    '''
    def __init__(self, product):
        self.product = product
        self.message = ""

    def execute_api(self):
        try:
            qs = ProductCode.objects.filter(name__icontains=self.product)
            if qs.count() == 0:
                self.message = f"搜尋「代碼 {self.product}」查無結果"
            else:
                message_list = list()
                for obj in qs:
                    message_list.append(f"{obj.category}：{obj.code} {obj.name}")
                self.message = f"{self.product} 代碼：\n" + "\n".join(message for message in message_list)
        except Exception as e:
            self.message = f"搜尋「代碼 {self.product}」發生錯誤"
        return self.message
