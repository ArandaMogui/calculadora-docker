# Imagen oficial de Python con version fija
FROM python:3.12.7-slim

# Directorio de trabajo dentro del contenedor
WORKDIR /app

# Copiar archivo de dependencias
COPY app/requirements.txt .

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copiar codigo de la aplicacion
COPY app/ .

# Documentar el puerto de la aplicacion
EXPOSE 5000

# Comando para iniciar Flask
CMD ["python", "app.py"]
