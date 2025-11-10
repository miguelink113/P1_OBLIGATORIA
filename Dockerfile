# 1. Usar la imagen base ligera de Python 3.11
FROM python:3.11-slim

# 2. Establecer la carpeta de trabajo dentro del contenedor
WORKDIR /app

# 3. Copiar el archivo de requisitos e instalar las dependencias
COPY acoplada/requirements_acoplada.txt .
RUN pip install --no-cache-dir -r requirements_acoplada.txt

# 4. Copiar los módulos de la aplicación
COPY model/ ./model/ 
COPY backend/ ./backend/

# 5. Copiar la aplicación principal (Flask)
COPY acoplada/app/ .

# 6. Documentar el puerto expuesto
EXPOSE 8080

# 7. Comando para ejecutar la aplicación
CMD ["python", "app_backend.py"]