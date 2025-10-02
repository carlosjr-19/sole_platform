# Imagen base de Python
FROM python:3.12-slim

WORKDIR /app

# Instalar dependencias del sistema necesarias para Chromium (Playwright)
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    ca-certificates \
    fonts-liberation \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libcups2 \
    libdbus-1-3 \
    libdrm2 \
    libgbm1 \
    libglib2.0-0 \
    libnspr4 \
    libnss3 \
    libx11-6 \
    libx11-xcb1 \
    libxcb1 \
    libxcomposite1 \
    libxdamage1 \
    libxext6 \
    libxfixes3 \
    libxrandr2 \
    libxshmfence1 \
    libxss1 \
    libxtst6 \
    lsb-release \
    xdg-utils \
    libpangocairo-1.0-0 \
    libpango-1.0-0 \
    libgtk-3-0 \
    libxkbcommon0 \
    --no-install-recommends && \
    rm -rf /var/lib/apt/lists/*

# Copiar e instalar dependencias Python
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Instalar Playwright y navegadores
RUN playwright install --with-deps chromium

# Copiar todo el código fuente
COPY . .

# Exponer puerto para Railway
ENV PORT=5000
EXPOSE $PORT

# Comando para ejecutar migraciones y levantar la app
CMD ["sh", "-c", "flask db upgrade && gunicorn --bind 0.0.0.0:$PORT 'sole_platform:create_app()'"]
