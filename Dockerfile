# Python 3.11.11 tabanlı bir Docker imajı kullan
FROM python:3.11.11

# Çalışma dizinini belirle
WORKDIR /app

# Gereksinimleri yükle
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# spaCy modelini indir
RUN python -m spacy download en_core_web_sm

# Uygulama dosyalarını kopyala
COPY . .

# Streamlit uygulamasını çalıştır
CMD ["streamlit", "run", "main.py", "--server.port=8080", "--server.enableCORS=false"]
