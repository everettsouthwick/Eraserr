FROM python:alpine

WORKDIR /app

COPY . .
RUN pip3 install --no-cache-dir -r requirements.txt

ENTRYPOINT ["python3", "app.py"]