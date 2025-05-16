FROM python:3.10

# Cài các gói hệ thống cần thiết để build dlib
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    python3-dev \
    libboost-all-dev \
    libopenblas-dev \
    liblapack-dev \
    libx11-dev \
    libgtk-3-dev \
    libjpeg-dev \
    libpng-dev \
    && rm -rf /var/lib/apt/lists/*

# Tạo thư mục làm việc
WORKDIR /app

# Copy requirements và code
COPY requirements.txt . 
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

# Cổng Render sẽ cấp qua biến môi trường PORT
ENV PORT=10000 

# Mở cổng (tùy chọn, không bắt buộc trong Dockerfile nhưng tốt để tài liệu rõ ràng)
EXPOSE $PORT

# Chạy Uvicorn, lấy PORT từ biến môi trường do Render cung cấp
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port $PORT"]
