# Usamos una imagen base oficial de Python (versión ligera)
FROM python:3.11-slim

# Establecemos el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copiamos el archivo de requerimientos primero para aprovechar la caché de Docker
COPY requirements.txt .

# Instalamos las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos el resto de los archivos de la carpeta actual (tu main.py) al contenedor
COPY . .

# Render expone el puerto dinámicamente a través de la variable $PORT
# Por defecto usaremos el 8000 si se corre de manera local
ENV PORT=8000
EXPOSE $PORT

# Comando para arrancar el servidor
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT}"]