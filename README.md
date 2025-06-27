# DanielBot Webhook + Copilot Endpoints

這是一個部署於 Google Cloud Run 的 FastAPI 專案，整合了 LINE Bot webhook、Copilot 系統警示、以及自然語言意圖辨識（NLU）三大功能。

---

## 🚀 API 路由

| 路徑              | 方法 | 說明                           |
|-------------------|------|--------------------------------|
| `/webhook`        | POST | 接收 LINE 訊息並自動回應         |
| `/copilot-alert`  | POST | Copilot 推送警示訊息入口         |
| `/copilot-nlu`    | POST | 回傳使用者文字的預測意圖與信心值 |

---

## 🔧 部署環境設定

| 項目       | 值                           |
|------------|------------------------------|
| 執行指令   | `uvicorn main:app --host=0.0.0.0 --port=8080` |
| Python 環境 | 3.10                         |
| 必要環境變數 | `LINE_CHANNEL_SECRET`、`LINE_CHANNEL_ACCESS_TOKEN` |

---

## 📦 專案結構範例

