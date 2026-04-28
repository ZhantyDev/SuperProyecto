# DockerFile de la API
# Usamos una versión estable de Python
FROM python:3.11-slim

# Directorio de trabajo dentro del contenedor
WORKDIR /app

# Copiamos los requisitos primero para aprovechar la caché de Docker
COPY requirements.txt .

# Instalamos las librerías
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos el resto del código de la API
COPY . .

# Exponemos el puerto de Flask
EXPOSE 5000

# Comando para arrancar la API
CMD ["python", "app.py"]