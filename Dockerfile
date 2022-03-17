FROM python:alpine

WORKDIR  /app

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

COPY . /app/

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080", "--log-level", "critical"]