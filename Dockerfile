FROM python:alpine

WORKDIR /app

ENV PYTHONUNBUFFERED 1

COPY . .
RUN pip3 install --no-cache-dir -r requirements.txt

CMD ["python3", "eraserr.py"]