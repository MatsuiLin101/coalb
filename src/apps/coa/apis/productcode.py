from .configs import *


class ProductCodeApiView(BasicApiView):
    '''
    作物代碼api介面
    (NEW)productcode(作物代碼)
    EXCEL匯入
    '''
    def __init__(self, params):
        self.message = ""
        try:
            self.command = params[0]
            self.product = params[1]
            self.command_text = f"{self.command} {self.product}"
        except Exception as e:
            raise CustomError("作物代碼的指令為「代碼 品項」，例如：\n「代碼 甘藍」")


    def execute_api(self):
        try:
            query_set = ProductCode.objects.filter(name__icontains=self.product)
            if query_set.count() == 0:
                self.message = f"「{self.command_text}」查無結果"
            else:
                message_list = list()
                for obj in query_set:
                    message_list.append(f"{obj.category}：{obj.code} {obj.name}")
                self.message = f"{self.product} 代碼：\n" + "\n".join(message for message in message_list)
            return self.message
        except Exception as e:
            traceback_log = TracebackLog.objects.create(app=f"{self.classname}", message=traceback.format_exc())
            self.message = f"「{self.command_text}」發生錯誤，錯誤編號「{traceback_log.id}」，請通知管理員處理"
            raise CustomError(self.message)
