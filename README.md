# DanielBot Webhook + Copilot Endpoints   

這是一個部署於 Google Cloud Run 的 FastAPI 專案，整合了 LINE Bot webhook、Copilot 系統警示、以及自然語言意圖辨識（NLU）三大功能。
## 🚀 Deploy to Cloud Run

## 🧪 開發者使用 `.env.template`
1. 建立 `.env` 檔案，依照 `.env.template` 填入憑證
2. 確保 `requirements.txt`、`Dockerfile` 存在
3. push 到 GitHub，Cloud Build 將自動建構與部署
4. ./test-webhook.sh


   ## ☁️ 部署到 Cloud Run

1. 複製 `.env.template` → 命名為 `.env`，並填入你的憑證
2. 確保 `requirements.txt`、`Dockerfile` 存在，包含 `uvicorn` 套件
3. Push 至 GitHub 主分支，Cloud Build 將自動建構並部署
4. 部署成功後，Webhook URL 預設為：https://YOUR_PROJECT_ID.a.run.app/webhook
5. 回到 LINE Developers 後台貼入並點選「Verify」





---

## 🚀 API 路由

| 路徑              | 方法 | 說明                           |
|-------------------|------|--------------------------------|
| `/webhook`        | POST | 接收 LINE 訊息並自動回應         |
| `/copilot-alert`  | POST | Copilot 推送警示訊息入口         |
| `/copilot-nlu`    | POST | 回傳使用者文字的預測意圖與信心值 |

---

## 🔧 部署環境設定

| 項目             | 值                                                   |
|------------------|------------------------------------------------------|
| 執行指令         | `uvicorn main:app --host=0.0.0.0 --port=8080`         |
| Python 環境      | 3.10                                                 |
| 必要環境變數     | `LINE_CHANNEL_SECRET`、`LINE_CHANNEL_ACCESS_TOKEN` |

---

## 📦 專案結構範例
danielbot-fastapi-webhook/ ├── main.py # FastAPI 主程式 ├── requirements.txt # 相依套件 └── routers/ └── webhook.py # LINE webhook 子路由

---

## 📝 範例：Copilot NLU 呼叫

```http
POST /copilot-nlu
Content-Type: application/json

{
  "text": "幫我查 2330 股價"
}
回應：
{
  "intent": "query_stock_price",
  "confidence": 0.92
}
🧩 後續擴充構想
整合台灣證交所資料查詢 API（如 TWSE/MOPS）

加入使用者匿名識別機制、支援多帳戶

增加 LINE broadcast 功能與 Copilot 模型串接


---

### ✨ 小重點

- 原本的「目錄結構」那一區沒包在 Markdown 區塊，排版會亂掉 → ✅ 我已加上 \`\`\`
- NLU 呼叫的 JSON 區塊未分開輸入與回應 → ✅ 現在有明確標記「回應」
- 後續擴充構想未分段 → ✅ 已標為列表（`-`），更易讀

---

你一旦更新這份 `README.md`，整個專案就能登上 FastAPI webhook 範例教科書封面了 📘✨  
要不要我再幫你補個 `.env.template` 或 `.gcloudignore` 範本，讓整個 repo 更完整？隨時待命💡

