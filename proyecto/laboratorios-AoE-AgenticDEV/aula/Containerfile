# Imagen OCI multi-stage. Se construye con Podman (sin licencia) y es
# compatible con Docker: `podman build -t aula:dev .`

FROM python:3.11-slim AS build
WORKDIR /build
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/instalacion -r requirements.txt

FROM python:3.11-slim AS runtime
RUN useradd --create-home --uid 10001 aula
COPY --from=build /instalacion /usr/local
WORKDIR /app
COPY src/ ./src/
COPY datos/ ./datos/
USER aula
ENV PYTHONPATH=/app/src
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=3s CMD python3 -c "import urllib.request;urllib.request.urlopen('http://localhost:8000/salud')"
CMD ["uvicorn", "aula.api.app:app", "--host", "0.0.0.0", "--port", "8000"]
