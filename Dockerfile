# Imagen base de Python
FROM python:3.10-slim

# Directorio de trabajo
WORKDIR /app

# Copiar requirements e instalar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código fuente
COPY . .

# Puerto expuesto (Railway usa $PORT)
EXPOSE $PORT

# Variables de entorno
ENV PORT=5000

# Comando para ejecutar con Gunicorn (para producción)
CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:$PORT app:app"]