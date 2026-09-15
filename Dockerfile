# Imagen base de Python
FROM python:3.12-slim

WORKDIR /app

# Copiar e instalar dependencias Python
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copiar todo el código fuente
COPY . .

# Exponer puerto para Railway
ENV PORT=5000
EXPOSE $PORT

# Comando para ejecutar migraciones y levantar la app
CMD ["sh", "-c", "flask db upgrade && gunicorn --timeout 120 --bind 0.0.0.0:$PORT 'sole_platform:create_app()'"]
