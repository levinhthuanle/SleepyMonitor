FROM python:3.10

# Cập nhật hệ thống và cài các gói cần thiết
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    libgtk2.0-dev \
    libboost-all-dev \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Tạo thư mục làm việc
WORKDIR /app

# Sao chép requirements trước để cache việc cài thư viện nếu code không đổi
COPY requirements.txt .

# Cài các thư viện Python (ưu tiên dlib trước để cache layer nặng nhất)
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Sao chép toàn bộ mã nguồn
COPY . .

# Expose cổng FastAPI
EXPOSE 8000

# Khởi chạy FastAPI
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
