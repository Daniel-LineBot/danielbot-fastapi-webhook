FROM python:3.10-slim

# 設定工作目錄 
WORKDIR /app

# 複製依賴檔並安裝套件
COPY requirements.txt .
RUN echo "[CloudBuild] 開始安裝 requirements.txt"
RUN pip install --no-cache-dir -r requirements.txt
RUN echo "[CloudBuild] requirements 安裝完畢 ✅"


# 複製剩餘程式碼
COPY . .

# 正確啟動 FastAPI 應用
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]


