import os

from celery import Celery

from django.conf import settings
from django.utils import timezone


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
@app.task
def delay_worker_test():
    print('delay worker test')
