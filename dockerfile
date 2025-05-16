FROM python:3.10-slim

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
COPY . .

# Cài thư viện Python
RUN pip install --no-cache-dir -r requirements.txt

# Mở cổng 8000
EXPOSE 8000

# Chạy FastAPI server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
