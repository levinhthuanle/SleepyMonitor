FROM danielgatis/dlib:python3.10

# Tạo thư mục làm việc
WORKDIR /app

# Copy requirements và code
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

# Mở cổng (Render sẽ tự set $PORT nên dùng biến môi trường)
EXPOSE 8000

# Chạy FastAPI server với biến $PORT của Render
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port $PORT"]
