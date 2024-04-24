# Etapa de construcción
FROM python:3.12.2 AS builder

# Actualizar pip
RUN pip install --upgrade pip

# Instalar dependencias necesarias para OpenCV y otras bibliotecas
RUN apt-get update && apt-get install -y libgl1-mesa-glx


# Establecer el directorio de trabajo en /app
WORKDIR /app

# Copiar los archivos de la aplicación al contenedor
COPY . /app

# Instalar las dependencias de la aplicación
RUN pip install --no-cache-dir -r requirements.txt

# Exponer el puerto 5000
EXPOSE 5000

# Ejecutar la aplicación cuando se inicie el contenedor
CMD ["python3", "main.py"]
