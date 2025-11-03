# Usamos una imagen base ligera de Python 3.11
FROM python:3.11-slim

# Establecer la carpeta de trabajo dentro del contenedor
WORKDIR /app

# Copiar el archivo de requisitos e instalar las dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# --- COPIA FINAL Y CRÍTICA ---
# Copia la carpeta 'app' (que contiene backend/ y model/)
# El contenido local de P1_OBLIGATORIA/app/ se copia a /app/app/ en el contenedor.
COPY app app

# Asegúrate de que tienes archivos __init__.py en app/, app/backend/ y app/model/

# --- FIN DE COPIA ---

# Documentar el puerto expuesto
EXPOSE 8080

# Comando para ejecutar la aplicación como un módulo: 'app.backend.app_backend'.
# La ruta del módulo ahora incluye 'app' porque está en /app/app/backend/
CMD ["python", "-m", "app.backend.app_backend", "--host", "0.0.0.0", "--port", "8080"]