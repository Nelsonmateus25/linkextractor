FROM       python:3.9-slim
LABEL      maintainer="LinkExtractor Python API"

WORKDIR    /app

COPY       requirements.txt /app/
RUN        pip install --no-cache-dir -r requirements.txt

COPY       linkextractor.py /app/
RUN        chmod a+x linkextractor.py

EXPOSE     5000
CMD        ["python", "linkextractor.py"]
