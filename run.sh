#!/usr/bin/env bash
# 在伺服器上執行 bot，程式結束後 5 秒自動重啟；輸出寫入 bot.log
cd "$(dirname "$0")"

while true; do
  .venv/bin/python -u bot.py >> bot.log 2>&1
  echo "[$(date '+%F %T')] bot 結束（exit $?），5 秒後重啟" >> bot.log
  sleep 5
done
