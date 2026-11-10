#!/usr/bin/env bash
# 在單一主機上執行的唯讀健康檢查（透過 ssh 'bash -s' < host_audit.sh 送過去）。
# 不會修改任何東西。
cd ~/coalb 2>/dev/null || { echo "## 找不到 ~/coalb"; exit 1; }
D="sudo -n docker"

echo "## 主機: $(hostname) $(uname -m) | $(grep PRETTY /etc/os-release | cut -d'"' -f2)"
echo "## 開機: $(uptime -p) | 負載: $(cut -d' ' -f1-3 /proc/loadavg)"
echo "## 磁碟 /: $(df -h / | awk 'NR==2{print $3"/"$2" ("$5")"}') | 記憶體: $(free -h | awk '/Mem/{print $3"/"$2}') | swap: $(free -h | awk '/Swap/{print $2}')"
echo "## 等待重開機: $([ -f /var/run/reboot-required ] && echo YES || echo no) | 可更新套件: $(apt list --upgradable 2>/dev/null | grep -c upgradable)（安全性: $(apt list --upgradable 2>/dev/null | grep -c -- -security)）"
echo "## ufw: $(sudo -n ufw status 2>/dev/null | head -1 | cut -d' ' -f2) | SSH 密碼登入: $(sudo -n sshd -T 2>/dev/null | awk '/^passwordauthentication/{print $2}')"
echo "## 程式版本: $(git branch --show-current) $(git log -1 --format='%h %ci %s') | 未提交變更: $(git status --short | wc -l)"
echo "## USE_ENV: $(grep -E '^USE_ENV=' src/envs/base.env | cut -d= -f2) | ALLOWED_HOSTS: $(grep -E '^ALLOWED_HOSTS=' src/envs/prod.env | cut -d= -f2)"
echo "## 容器:"
$D ps -a --format '{{.Names}}\t{{.Status}}' 2>&1 | sed 's/^/   /'
echo "## 憑證:"
sudo -n certbot certificates 2>/dev/null | awk '/Certificate Name/{n=$3} /Expiry Date/{print "   "n" 到期 "$3"（剩 "$6" 天）"}'
echo "## Certbot 自動續約 timer: $(systemctl list-timers 2>/dev/null | grep -c certbot) 個"
echo "## 資料庫備份: $(ls pgdata/backup 2>/dev/null | wc -l) 個檔案，最新: $(ls -t pgdata/backup 2>/dev/null | head -1)"
echo "## Celery worker: $($D logs --since 24h coalb_wk 2>&1 | grep -c 'succeeded') 個成功、$($D logs --since 24h coalb_wk 2>&1 | grep -cE 'raised|ERROR') 個錯誤（24 小時內）"
LOG=container/prod/nginx/logs
for f in $LOG/*access.log; do
  [ -s "$f" ] || continue
  last=$(tail -1 "$f" | awk '{print substr($4,2)}')
  echo "## $(basename $f): 最後一筆 $last | 今天 $(grep -c "$(date -u +%d/%b/%Y)" "$f") 筆"
done
echo "## nginx log 大小: $(du -sh $LOG 2>/dev/null | cut -f1)"
