# coalb — 動態查詢小幫手（LINE Bot）

使用者在 LINE 輸入指令（例如 `產地 屏東 芒果 113/7`），後端用 Selenium 即時爬農業部等政府網站，或查本地資料表，回傳農業統計數據。全部用正體中文回覆。

## 技術組成

- Django 2.2 + Python 3.9.19 + PostgreSQL 10 + Redis 5 + Celery 5 + Selenium 4.4（遠端 `seleniarm/standalone-chromium:123.0` 容器，ARM 版）+ line-bot-sdk 1.19
- docker-compose：`container/dev/`（開發）、`container/prod/`（正式）。容器名稱：`coalb_web`、`coalb_wk`（Celery）、`coalb_db`、`coalb_rd`、`coalb_nginx`、`coalb_selenium`
- `systemd/`、`nginx/sites-available/` 是改用 Docker 前的舊部署方式，已不使用

## 程式結構

| 位置 | 說明 |
|---|---|
| `src/apps/line/views.py` | LINE webhook（`/line/callback/`），分派文字、檔案、貼圖、加好友事件 |
| `src/apps/coa/views.py` | `get_reply_from_text()`：用 if/elif 把指令分派給各 ApiView；另有上傳頁、`proxy_parser`、`proxy_build` |
| `src/apps/coa/apis/` | 每類指令一個 `*ApiView`。`__init__.py` 的註解寫了各指令的資料來源和已知問題 |
| `src/apps/coa/apis/configs.py` | 共用基底類別：`BasicApiView`（動態查詢）、`AnnualReportBasicApiView`（下載年報 ods 再解析） |
| `src/apps/coa/builders/` | 先把網站的下拉選項爬進資料表（樹狀的 parent/main_class/sub_class 模型） |
| `src/core/celery.py` | `delay_proxy_parser`：代理站在背景執行爬蟲並寫入快取 |
| `src/apps/line/webhook.py` | 直接複製進來的 linebot SDK 原始碼，不要修改 |

## 兩台正式主機（重要）

同一份程式部署在兩台主機，用 `src/envs/base.env` 的 `USE_ENV=prod.env` 載入設定。**兩台的 `prod.env` 檔名相同、內容不同**，主機角色就是靠這個區分的（`proxy.env` 實際上沒有使用）。

| | 主站 | 代理站 |
|---|---|---|
| 網域 | coalb.mlozo.com | proxycoalb.mlozo.com |
| 主機 | Oracle VPS（美國 IP，ARM） | 使用者區網的樹莓派 4（台灣 IP） |
| SSH | `ssh -i /Users/coder/Desktop/mlozo/ssh/oracle-coalb-ssh-key ubuntu@144.24.60.152` | `ssh farmer@192.168.3.180` |
| 專案路徑 | `~/coalb` | `~/coalb` |

- 兩台都要用 `sudo docker ...`，因為使用者不在 docker 群組
- 兩個網域前面都有 Cloudflare；主機上的 nginx 搭配 Certbot 處理 TLS，再轉到容器的 8000 port
- **代理機制**：政府網站擋海外 IP，所以主站把部分查詢用 HTTPS 打到代理站的 `/coa/proxy/parser/?token=PROXY_TOKEN&api=...`。代理站查 Redis 快取，沒有資料時丟給 Celery 去爬，**第一次只會回「抓取資料中，請稍後再試。」**，約 30 秒後再查一次才拿得到結果。錯誤通知信也是經代理站寄出的（`core/log.py`）
- 目前經代理的查詢：產地價（`CropPriceOriginApiView`）、作物產量和種植面積（`CropProduceTotalApiView`），以及這兩個對應的 builder
- 對兩台主機：唯讀檢查可以直接做；重開機、`docker compose` 重啟或重建、改設定、寫資料庫、部署之前，要先問使用者

## 驗證查詢功能

在主站容器裡直接呼叫機器人處理訊息的函式，流程跟真實使用者一樣，但不會發 LINE 訊息：

```bash
ssh -i /Users/coder/Desktop/mlozo/ssh/oracle-coalb-ssh-key ubuntu@144.24.60.152 \
  'sudo docker exec coalb_web python manage.py shell -c "from apps.coa.views import get_reply_from_text as g; print(g(\"總產值 113\"))"'
```

- 不帶參數輸入指令（例如 `產量`）會回傳該指令的用法
- 失敗時回覆裡會有錯誤編號，可以到 `apps.log.models.TracebackLog` 用 id 查詳細錯誤
- 長時間的批次測試要在主機上用 `nohup` 背景執行並寫到檔案，SSH 連線可能中途斷掉

## 已知狀態（2026-11-10）

- **agrstat.moa.gov.tw 改版**：舊網址 `/sdweb/public/...` 變成 404，新網站在 `/moasdweb/...`，頁面結構全部換掉。所有用 agrstat 的指令都失效：
  - 年報（`Book.aspx`）：產值、生產毛額、農家所得、農牧戶、耕地面積、災害
  - 動態查詢（`InquireAdvance.aspx`）：總產值、就業人口、農保、老農津貼、獎助學金、批發、生產成本、工時、飼養場數、在養量、屠宰量、副產物
  - 新網站沒有擋海外 IP
- **毛豬網站 `ppg.naif.org.tw`**：沒有改版，但開始擋海外 IP，從台灣 IP 連正常。修法是把它接上代理機制，網址改成 https
- **正常的功能**：產地、產量、種植面積（經代理）、單位產值、單位產量、作物代碼（本地資料表）、拍賣價、零售價（`price.naif.org.tw`）
- 兩台主機都沒有資料庫備份、都在等重開機套用更新、都沒有監控；樹莓派曾兩度整月離線（2025 年 10～11 月、2026 年 9 月）

## 開發慣例

- **分支流程（git flow）**：
  1. 開發新功能時，從 `develop` 開 `feature/<說明>` 分支，在該分支上開發
  2. 測試時，把測試環境的分支切換到這個開發分支
  3. 開發完成後，merge 回 `develop`
  4. 要部署到正式機時，從 `develop` 走 release 流程 merge 到 `master`
  5. 緊急修正走 `hotfix/hX.Y.Z-說明`，修完 merge 回 `master` 和 `develop`
- **merge 一律用 `--no-ff`**，保留分支的合併紀錄；不要 fast-forward，也不要 rebase 到目標分支
- tag 格式為 `vX.Y.Z-說明`（release）或 `hX.Y.Z-說明`（hotfix）
- 不要直接在 `develop` 或 `master` 上開發功能
- commit 訊息用 `feat:` / `fix:` / `docs:` 等前綴加英文短句
- Lint：`make format`，也就是 flake8，設定見根目錄 `Makefile`。測試幾乎沒有，`tests.py` 裡只有 print
- 使用者看到的訊息、程式註解、docstring 都用正體中文
- 爬蟲用元素 ID 或固定 XPath 定位，網站改版就會失效；修的時候優先改成依欄位標題定位

## 機密資料

`src/.env*`、`src/envs/*.env`、`container/prod/nginx/ssl*`、`pgdata/`、`backup/`、`src/backup/` 裡有密碼、token 和正式資料庫匯出檔。只能看變數名稱，或用遮蔽方式查看（例如 `sed -E 's/(TOKEN|SECRET|PASSWORD)([^=]*)=.*/\1\2=***/'`），不要印出或傳送原始值。
