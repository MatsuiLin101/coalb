#!/usr/bin/env bash
# 對 coalb 兩台正式主機做唯讀健康檢查，並從本機打兩個網域的健康檢查端點。
set -uo pipefail
DIR=$(cd "$(dirname "$0")" && pwd)
MAIN_HOST=${COALB_MAIN_HOST:-ubuntu@144.24.60.152}
MAIN_KEY=${COALB_MAIN_KEY:-/Users/coder/Desktop/mlozo/ssh/oracle-coalb-ssh-key}
PROXY_HOST=${COALB_PROXY_HOST:-farmer@192.168.3.180}
SSH_OPTS=(-o BatchMode=yes -o ConnectTimeout=10)

echo "==================== 主站 coalb.mlozo.com（$MAIN_HOST）"
ssh -i "$MAIN_KEY" "${SSH_OPTS[@]}" "$MAIN_HOST" 'bash -s' < "$DIR/host_audit.sh" 2>&1 || echo "!! 無法連線到主站"

echo
echo "==================== 代理站 proxycoalb.mlozo.com（$PROXY_HOST）"
ssh "${SSH_OPTS[@]}" "$PROXY_HOST" 'bash -s' < "$DIR/host_audit.sh" 2>&1 || echo "!! 無法連線到代理站（樹莓派可能離線，或這台電腦不在同一個區網）"

echo
echo "==================== 對外連線"
for u in https://coalb.mlozo.com/line/ https://proxycoalb.mlozo.com/line/; do
  printf '%-40s %s\n' "$u" "$(curl -s -m 15 -o /dev/null -w 'HTTP %{http_code} %{time_total}s' "$u" || echo 連線失敗)"
done
printf '%-40s %s\n' "主站 -> 代理站" "$(ssh -i "$MAIN_KEY" "${SSH_OPTS[@]}" "$MAIN_HOST" "curl -s -m 15 -o /dev/null -w 'HTTP %{http_code} %{time_total}s' https://proxycoalb.mlozo.com/line/" 2>&1 || echo 連線失敗)"
