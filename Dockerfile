# Imagen base de Python
FROM python:3.12-slim

# Establece el directorio de trabajo
WORKDIR /app

# Actualizar e instalar dependencias del sistema mínimo
RUN apt-get update && \
    apt-get install -y build-essential && \
    rm -rf /var/lib/apt/lists/*

# Copiar e instalar las dependencias Python
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copiar todo el código fuente al contenedor
COPY . .

# Exponer el puerto que usará la app (Railway usa $PORT)
EXPOSE $PORT
ENV PORT=5000

# Comando para ejecutar migraciones y luego Gunicorn
CMD ["sh", "-c", "flask db upgrade && gunicorn --bind 0.0.0.0:$PORT 'sole_platform:create_app()'"]
