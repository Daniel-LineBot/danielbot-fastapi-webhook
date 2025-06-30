#!/bin/bash

# 載入環境變數
if [ -f .env ]; then
  export $(grep -v '^#' .env | xargs)
else
  echo "❌ 找不到 .env 檔案，請先建立並填入 LINE 憑證"
  exit 1
fi

# 測試 webhook URL 是否存在
if [ -z "$WEBHOOK_URL" ]; then
  echo "❌ 未設定 WEBHOOK_URL，請在 .env 中加入"
  exit 1
fi

echo "🚀 發送 webhook 測試請求到：$WEBHOOK_URL"

curl -X POST "$WEBHOOK_URL" \
  -H "Content-Type: application/json" \
  -H "X-Line-Signature: dummy-signature" \
  -d '{"events": [], "destination": "Uxxxxxxxxxxxxxx"}'

echo -e "\n✅ 測試請求已送出，請查看 Cloud Run log 或 LINE Developers 是否收到事件"
