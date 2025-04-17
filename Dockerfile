# Temel imaj
FROM python:3.10

# Gerekli sistem bağımlılıkları (PyQt5 için X11 ve diğerleri)
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libxkbcommon-x11-0 \
    x11-xserver-utils \
    && rm -rf /var/lib/apt/lists/*

# Uygulama dosyalarını kopyala
WORKDIR /app
COPY . .

# Gerekli Python paketleri
RUN pip install --no-cache-dir -r requirements.txt

# Başlatma komutu
CMD ["python", "main.py"]
