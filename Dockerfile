
FROM python:3.11-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1
ENV KERAS_HOME=/root/.keras

COPY requirements.txt .

RUN python -m pip install --upgrade pip && \
    pip install -r requirements.txt

# Download and cache pretrained MobileNetV2 weights
# while building the image.
RUN python -c "from tensorflow.keras.applications import MobileNetV2; MobileNetV2(weights='imagenet')"

COPY app.py .

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "1", "--threads", "4", "--timeout", "120", "app:app"]
