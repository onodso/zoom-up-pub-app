FROM python:3.11-slim

WORKDIR /app

# 依存関係インストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションコード
COPY . .

EXPOSE 8000

# 本番環境では --reload を削除してください
# 開発環境: uvicorn main:app --host 0.0.0.0 --port 8000 --reload
# 本番環境: uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
