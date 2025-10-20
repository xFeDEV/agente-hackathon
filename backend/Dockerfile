# Imagen base oficial de Python 3.12 slim
FROM python:3.12-slim-bookworm

# Establecer directorio de trabajo dentro del contenedor
WORKDIR /app

# Variable de entorno para logs en tiempo real
ENV PYTHONUNBUFFERED=1

# Copiar archivo de dependencias
COPY requirements.txt .

# Instalar dependencias sin caché para reducir tamaño de imagen
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código de la aplicación al contenedor
COPY ./app /app

# El comando de inicio se define en docker-compose.yml para permitir hot-reloading
