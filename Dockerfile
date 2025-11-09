# 1. Usar la imagen base ligera de Python 3.11
# Esta imagen es adecuada para aplicaciones web basadas en frameworks como Flask.
FROM python:3.11-slim

# 2. Establecer la carpeta de trabajo dentro del contenedor
WORKDIR /app

# 3. Copiar el archivo de requisitos e instalar las dependencias
# ¡CORRECCIÓN! El archivo está dentro de la carpeta 'acoplada' respecto al contexto.
COPY acoplada/requirements_acoplada.txt .
RUN pip install --no-cache-dir -r requirements_acoplada.txt

# 4. Copiar los módulos de la aplicación
# Estos están en la raíz del contexto (P1_OBLIGATORIA), así que la ruta es correcta.
COPY model/ ./model/ 
COPY backend/ ./backend/

# 5. Copiar la aplicación principal (Flask)
# El código de la aplicación (app_backend.py) está dentro de 'acoplada/app/'
COPY acoplada/app/ .

# 6. Documentar el puerto expuesto
EXPOSE 8080

# 7. Comando para ejecutar la aplicación (VUELVE A LA VERSIÓN ORIGINAL)
# Esto ejecuta la aplicación usando el servidor de desarrollo de Flask (app.run)
CMD ["python", "app_backend.py"]