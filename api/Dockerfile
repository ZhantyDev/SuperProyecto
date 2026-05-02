# DockerFile de la API
# Usamos la imagen de Spark de Bitnami que ya tiene Spark instalado
FROM public.ecr.aws/bitnami/spark:3.5

# Usuario root para instalar paquetes
USER root

# Directorio de trabajo dentro del contenedor
WORKDIR /app

# Copiamos los requisitos primero para aprovechar la caché de Docker
COPY requirements.txt .

# Instalamos las librerías de Python adicionales
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos el resto del código de la API
COPY . .

# Exponemos el puerto de Flask
EXPOSE 5000

# Comando para arrancar la API
CMD ["python", "app.py"]