FROM python:3.12-slim

WORKDIR /app/frontend

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY frontend/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

COPY frontend /app/frontend

EXPOSE 7860

CMD ["python", "app.py"]
