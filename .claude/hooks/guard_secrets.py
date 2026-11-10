#!/usr/bin/env python3
"""
PreToolUse hook（Bash）：擋下會把 .env 機密原文印出來的指令。

規則：指令只要提到 env 檔（src/.env、src/.env-prod.、src/envs/*.env，本機或透過 ssh 都算），
就必須符合以下其中一種「安全讀法」，否則擋下（exit 2）：
  - 遮蔽值：輸出前把值換成 ***（例如 sed -E 's/(TOKEN|SECRET|PASSWORD)=.*/\\1=***/'）
  - 只比對雜湊：shasum / sha256sum / md5
  - 只看變數名稱：cut -d= -f1、sed 's/=.*//'、awk -F= '{print $1}'
  - 只計數：grep -c、wc
  - 只讀明確列出、而且名稱不含機密字樣的變數（例如 grep -E "^(ALLOWED_HOSTS|DOMAIN)="）
  - 不讀內容的檔案操作：ls、test、stat、git status 之類
"""
import json
import re
import sys

ENV_FILE = re.compile(r"(?:^|[\s/'\"=])(?:src/)?(?:envs/[\w.-]*\.env|\.env(?:-prod\.?)?)(?=$|[\s'\"\\;|&)])")
READERS = re.compile(r"(?:^|[\s;&|('\"])(cat|head|tail|less|more|bat|grep|egrep|rg|awk|sed|strings|xxd|od|base64|cp|scp|rsync|python3?|perl|source|env|\.)(?=\s)")
SECRET_WORD = re.compile(r"TOKEN|SECRET|PASSWORD|PASSWD|PASS\b|_KEY|KEY=|PRIVATE", re.I)

SAFE_PATTERNS = [
    re.compile(r"\*\*\*"),                                  # 遮蔽成 ***
    re.compile(r"\b(shasum|sha256sum|sha1sum|md5|md5sum)\b"),  # 雜湊
    re.compile(r"cut\s+-d\s*['\"]?=['\"]?\s+-f\s*1\b"),     # 只取變數名稱
    re.compile(r"sed\s+(-E\s+)?['\"]s/=\.\*//"),
    re.compile(r"awk\s+-F\s*['\"]?=['\"]?\s+['\"]\{\s*print\s+\$1"),
    re.compile(r"\bgrep\s+(-\w*\s+)*-\w*c\b"),              # grep -c
    re.compile(r"\|\s*wc\b"),
]
# grep 只抓明確列出的變數名稱，例如 grep -E "^(ALLOWED_HOSTS|DOMAIN)=" 或 grep "^DEBUG="
EXPLICIT_KEYS = re.compile(r"\^\(?([A-Z0-9_|]+)\)?=")


def is_safe(cmd: str) -> bool:
    if any(p.search(cmd) for p in SAFE_PATTERNS):
        return True
    keys = EXPLICIT_KEYS.findall(cmd)
    if keys and "grep" in cmd and not any(SECRET_WORD.search(k) for k in keys):
        # 只讀非機密變數；但要求沒有其他讀取整個檔案的指令
        others = re.sub(r"\bgrep\b[^|;&]*", "", cmd)
        return not re.search(r"\b(cat|head|tail|less|more|bat|strings|xxd|base64|cp|scp|rsync)\b", others)
    return False


def main() -> int:
    try:
        data = json.load(sys.stdin)
    except Exception:
        return 0
    cmd = (data.get("tool_input") or {}).get("command") or ""
    if not ENV_FILE.search(cmd) or not READERS.search(cmd):
        return 0
    if is_safe(cmd):
        return 0
    print(
        "已擋下：這個指令可能會把 .env 裡的機密原文印出來。"
        "請改用遮蔽讀法（sed -E 's/(TOKEN|SECRET|PASSWORD)([^=]*)=.*/\\1\\2=***/'）、"
        "只看變數名稱（cut -d= -f1）、比對雜湊（shasum），或只 grep 明確列出的非機密變數。"
        "規則見 .claude/hooks/guard_secrets.py。",
        file=sys.stderr,
    )
    return 2


if __name__ == "__main__":
    sys.exit(main())
