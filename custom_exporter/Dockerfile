FROM python:3.11

COPY exporter.py /app/exporter.py
COPY requirements.txt /app/requirements.txt
WORKDIR /app
RUN pip install --no-cache-dir -r requirements.txt
ENV HITL_URL $HITL_URL
CMD ["python3", "exporter.py"]
