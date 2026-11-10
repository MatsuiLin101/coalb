---
name: verify-queries
description: 在 coalb 主站（正式機）實際跑一輪所有 LINE 機器人查詢指令，整理成正常／失敗清單和失敗原因。用在修好或修改查詢功能後的回歸測試、merge 回 develop 前的檢查，或使用者問「查詢功能是不是都還正常」的時候。
---

# 驗證 coalb 所有查詢功能

在主站 `coalb_web` 容器裡逐一呼叫 `get_reply_from_text()`。流程跟真實 LINE 使用者一樣，但**不會發送任何 LINE 訊息**，只會新增 `TracebackLog`、`ProxyLog` 紀錄和 Redis 快取。這是唯讀驗證，可以直接執行，不需要先問使用者。

## 步驟

1. 在背景執行（要跑 10～30 分鐘，主要花在爬蟲等待）。輸出檔放在 scratchpad：

   ```bash
   bash .claude/skills/verify-queries/run.sh <scratchpad>/query-test.tsv
   ```

   用 Bash 的 `run_in_background`，等完成通知，不要輪詢。

2. 讀取 TSV。每行格式是 `狀態 \t 秒數 \t 查詢 \t 回覆摘要`：

   | 狀態 | 意思 |
   |---|---|
   | OK | 有資料 |
   | EMPTY | 查詢成功但查無資料，通常是參數問題（年份太新、品項名稱），不一定是壞掉 |
   | PENDING | 經代理的查詢，重試 3 次後仍在爬，可能是樹莓派或 Celery 有問題 |
   | FAIL | 「該功能維護中」，主站呼叫代理失敗（代理站離線或 token 錯誤） |
   | ERROR | 未知錯誤，摘要裡有錯誤編號 |
   | USAGE | 參數格式不對，回傳的是用法說明，要修的是測試清單 |

3. 對 ERROR 項目，到主站查 TracebackLog，找出實際的 Python 例外（略過 Chrome 的 stacktrace）：

   ```bash
   ssh -i /Users/coder/Desktop/mlozo/ssh/oracle-coalb-ssh-key ubuntu@144.24.60.152 \
     'sudo docker exec coalb_web python manage.py shell -c "
   from apps.log.models import TracebackLog as T
   for i in [<編號>]:
       L=T.objects.get(id=i).message.splitlines()
       idx=[n for n,l in enumerate(L) if \"Exception\" in l or \"Error\" in l]
       s=max(0,(idx[0] if idx else len(L))-6); print(\"=== #%d\" % i); print(chr(10).join(L[s:(idx[0]+3 if idx else s+10)]))
   "'
   ```

   常見原因：`TimeoutException` 或 `NoSuchElementException` 表示網站改版；`ERR_CONNECTION_REFUSED` 表示網站擋海外 IP，可以從樹莓派連看看來確認。

4. 回報給使用者：先講正常幾個、失敗幾個，再依失敗原因分組列出指令，最後拿來跟 `CLAUDE.md`「已知狀態」比較，指出新壞掉的和新修好的。

## 維護

- 查詢清單在 `query_test.py` 的 `QUERIES`。新增或修改指令時要一起更新，年份用政府網站上一定有資料的年份（通常是前 1～2 年）。
- 主機或金鑰變了，可以用環境變數 `COALB_MAIN_HOST`、`COALB_MAIN_KEY` 覆寫，或直接修改 `run.sh`。
