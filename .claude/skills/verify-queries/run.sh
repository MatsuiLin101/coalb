#!/usr/bin/env bash
# 在主站背景執行 query_test.py，等它跑完後把 TSV 結果存到本機。
# 用法：run.sh <本機輸出檔路徑>
# 環境變數可覆寫：COALB_MAIN_HOST、COALB_MAIN_KEY
set -euo pipefail

OUT=${1:?需要指定本機輸出檔路徑}
HOST=${COALB_MAIN_HOST:-ubuntu@144.24.60.152}
KEY=${COALB_MAIN_KEY:-/Users/coder/Desktop/mlozo/ssh/oracle-coalb-ssh-key}
DIR=$(cd "$(dirname "$0")" && pwd)
REMOTE_PY=/tmp/coalb_query_test.py
REMOTE_OUT=/tmp/coalb_query_test.out

r() { ssh -i "$KEY" -o BatchMode=yes -o ConnectTimeout=15 -o ServerAliveInterval=30 "$HOST" "$@"; }

scp -q -i "$KEY" -o BatchMode=yes "$DIR/query_test.py" "$HOST:$REMOTE_PY"

# 用 nohup 在主機上背景執行，SSH 中途斷線也不會中斷測試
r "sudo -n docker cp $REMOTE_PY coalb_web:$REMOTE_PY && rm -f $REMOTE_OUT && \
   (nohup sh -c 'sudo -n docker exec -w /code coalb_web python $REMOTE_PY > $REMOTE_OUT 2>&1; echo __DONE__ >> $REMOTE_OUT' >/dev/null 2>&1 &)"
echo "已在主站開始執行，等待完成（最多約 40 分鐘）..." >&2

done_flag=0
for _ in $(seq 1 120); do
  if r "grep -q __DONE__ $REMOTE_OUT" 2>/dev/null; then done_flag=1; break; fi
  sleep 20
done

r "grep -E \$'^(OK|EMPTY|PENDING|FAIL|ERROR|USAGE)\t' $REMOTE_OUT; \
   grep -iE 'Traceback|Error' $REMOTE_OUT | grep -vE \$'^(OK|EMPTY|PENDING|FAIL|ERROR|USAGE)\t' | head -5 >&2; \
   sudo -n docker exec coalb_web rm -f $REMOTE_PY; rm -f $REMOTE_PY; \
   if grep -q __DONE__ $REMOTE_OUT; then rm -f $REMOTE_OUT; fi" > "$OUT"

if [ ! -s "$OUT" ]; then
  echo "失敗：沒有任何結果，請看上面的錯誤訊息，或到主機上查看 $REMOTE_OUT" >&2
  exit 4
fi
if [ "$done_flag" != 1 ]; then
  echo "警告：等待逾時，結果可能不完整（主機上的 $REMOTE_OUT 仍在寫入）" >&2
  exit 3
fi
echo "完成，結果已存到 $OUT" >&2
cut -f1 "$OUT" | sort | uniq -c >&2
