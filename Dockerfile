# 1. Capa base: Usamos el silicio más ligero y actual de Python 3.14
FROM python:3.14-slim

# 2. Evitamos que Python genere archivos de caché (.pyc) y forzamos la salida estándar
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 3. Definimos el área de trabajo en el chasis
WORKDIR /app

# 4. Copiamos solo la lista de materiales primero (optimización de caché de Docker)
COPY requirements.txt .

# 5. Soldamos los componentes (Instalamos dependencias)
RUN pip install --no-cache-dir -r requirements.txt

# 6. Copiamos el resto del circuito (nuestro código fuente)
COPY . .

# 7. Exponemos el pin de red (Puerto 8000)
EXPOSE 8000

# 8. Encendemos el procesador usando ASGI
CMD ["uvicorn", "src.dev_pulse.main:app", "--host", "0.0.0.0", "--port", "8000"]
