# Manual de arranque — Aula

## Requisitos

- Python 3.11.
- Dependencias: `python3 -m pip install -r requirements.txt`.

## Preparación

Desde la carpeta `aula`:

```bash
python3 herramientas/generar_corpus.py
python3 -m pytest tests/ -q
```

El corpus generado es sintético y determinista.

## Arranque local

```bash
PYTHONPATH=src uvicorn aula.api.app:app --host 127.0.0.1 --port 8001
```

El servicio queda expuesto únicamente en `http://127.0.0.1:8001`.

## Comprobación

```bash
python3 -c "import urllib.request; print(urllib.request.urlopen('http://127.0.0.1:8001/salud').read().decode())"
```

La respuesta debe contener `"estado": "ok"`.

## Recursos HTTP

- `GET /salud`
- `POST /matriculas`
- `GET /expedientes/{estudiante_id}`

La documentación interactiva está disponible en `http://127.0.0.1:8001/docs`.

## Detención

Pulsa `Ctrl+C` en la terminal de Uvicorn.
