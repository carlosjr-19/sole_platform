# Imagen base de Python
FROM python:3.12-slim

# Establece el directorio de trabajo
WORKDIR /app

# Copiar e instalar las dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar todo el código fuente al contenedor
COPY . .

# Exponer el puerto que usará la app (Railway usa $PORT)
EXPOSE $PORT

# Definir variable de entorno para el puerto por defecto
ENV PORT=5000

# Comando para ejecutar Gunicorn (apuntando a app:app)
CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:$PORT app:app"]