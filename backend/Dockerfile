FROM python:3.13-slim

WORKDIR /app

COPY requirements.list .
RUN pip install --no-cache-dir -r requirements.list

COPY . .

EXPOSE 2137

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "2137"]