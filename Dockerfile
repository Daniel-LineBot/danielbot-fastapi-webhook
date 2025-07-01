FROM python:3.10-slim

# 設定工作目錄
WORKDIR /app
COPY . .  # 這要能把 main.py 複製進來


# 複製依賴檔並安裝套件
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 複製剩餘程式碼
COPY . .

# 正確啟動 FastAPI 應用
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]


