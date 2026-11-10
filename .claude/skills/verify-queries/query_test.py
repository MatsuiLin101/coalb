# 在 coalb_web 容器內以 `python query_test.py` 執行（工作目錄 /code）。
# 不用 `manage.py shell < 檔案`：Django 2.2 的 shell 用獨立的 locals 執行 stdin，
# 檔案裡定義的函式互相呼叫時會 NameError。
# 逐一呼叫機器人處理訊息的 get_reply_from_text()，不會發送 LINE 訊息；
# 只會新增 TracebackLog / ProxyLog 紀錄與 Redis 快取。
# 輸出 TSV：狀態 \t 秒數 \t 查詢 \t 回覆摘要
#   OK      有資料
#   EMPTY   查詢成功但查無資料（參數可能需要調整）
#   PENDING 代理還在爬（重試後仍是這樣才會留下）
#   FAIL    回覆「該功能維護中」，代理呼叫失敗
#   ERROR   未知錯誤，摘要裡有 TracebackLog 編號
#   USAGE   參數格式不對，回傳的是用法說明
import os
import re
import sys
import time
import warnings

warnings.filterwarnings("ignore")
sys.path.insert(0, "/code")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
import django  # noqa: E402

django.setup()
from apps.coa.views import get_reply_from_text  # noqa: E402

# 每行一個查詢；年份用民國年。新增或修改指令時，記得一起更新這份清單。
QUERIES = """
產值 稻米 113
總產值 113
總產值 台中 113
生產毛額 113
農家所得 113
農牧戶 113
耕地面積 113
就業人口 113
就業人口 114/6
災害 113
農保 113
農保 高雄 114/6
老農津貼 113/6
獎助學金 113
產地 芒果 113
產地 屏東 芒果 113/7
批發 甘藍 113
批發 甘藍 114/6
產量 雲林 落花生 113
種植面積 雲林土庫 落花生 113
產量 雞蛋 113
單位產值 屏東 香蕉
單位產量 雲林二崙 香蕉
成本 香蕉 113
工時 香蕉 113
毛豬 113
毛豬 114/6
價格 豬 114/6
拍賣價 羊 113
零售價 雞蛋 113
場數 豬 113
在養量 豬 113
屠宰 豬 113
屠宰 鴨 113 彰化
副產物 蜂蜜 113
代碼 甘藍
""".strip().splitlines()

PENDING_RETRIES = 3
PENDING_WAIT = 45


def classify(reply):
    if "抓取資料中" in reply:
        return "PENDING"
    if "維護中" in reply:
        return "FAIL"
    if "錯誤編號" in reply:
        return "ERROR"
    if "結果如下" in reply:
        body = reply.split("結果如下", 1)[1]
        has_number = re.search(r"\d[\d,]*(\.\d+)?\s*\(", body) or re.search(r"[：:]\s*[A-Z]?\d", body)
        return "OK" if has_number else "EMPTY"
    if "無法搜尋" in reply or "指令為" in reply:
        return "USAGE"
    return "ERROR"


def run(query):
    start = time.time()
    try:
        reply = get_reply_from_text(query)
    except Exception as e:  # CustomError 的訊息就是要回給使用者的文字
        reply = str(e)
    return classify(reply), time.time() - start, reply


results = {q: run(q) for q in QUERIES}

for attempt in range(PENDING_RETRIES):
    pending = [q for q, r in results.items() if r[0] == "PENDING"]
    if not pending:
        break
    time.sleep(PENDING_WAIT)
    for q in pending:
        results[q] = run(q)

for q in QUERIES:
    status, seconds, reply = results[q]
    excerpt = reply.replace("\n", " | ").replace("\t", " ")[:220]
    print(f"{status}\t{seconds:.1f}\t{q}\t{excerpt}", flush=True)
