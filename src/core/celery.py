import os
import traceback

from celery import Celery
from celery import shared_task

from django.conf import settings


# 設置環境變量 DJANGO_SETTINGS_MODULE
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

# 創建實例
app = Celery('core')
app.config_from_object('django.conf:settings')

# 查找在 INSTALLED_APPS 設置的異步任務
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


# ================== 排程任務[Start] ==================
app.conf.beat_schedule = {}


# ================== MessageQueue任務[Start] ==================
@shared_task(name='worker_test')
def delay_worker_test():
    print('delay worker test')
    return True


@app.task
def delay_proxy_parser(api: str, params: list):
    from django.core.cache import cache
    from apps.coa.apis.cropprice import CropPriceOriginApiView
    from apps.coa.apis.cropproduce import CropProduceTotalApiView
    from apps.log.models import TracebackLog

    try:
        # 如果 cache 中有資料，則直接從 cache 取得資料
        response = cache.get(' '.join(params))

        # 如果 cache 中的資料存在且 TTL 大於 60 分鐘，則直接返回
        # 否則，重新執行 API 並更新 cache
        if response and cache.ttl(' '.join(params)) >= 60 * 60:
            return response

        if api == 'CropPriceOriginApiView':
            api_class = CropPriceOriginApiView
        elif api == 'CropProduceTotalApiView':
            api_class = CropProduceTotalApiView
        else:
            return 'API not found'

        obj = api_class(params)
        response = obj.execute_api()

        cache.set(' '.join(params), response, timeout=60 * 60 * 24)
        return response
    except Exception as e:
        TracebackLog.objects.create(app='delay_proxy_parser', message=traceback.format_exc())
        return str(e)
