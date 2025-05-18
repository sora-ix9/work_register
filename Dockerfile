# Select base image from which we build the container
FROM python:3.11.9-slim
ENV TZ=Asia/Bangkok

# Copy application code into the container
COPY ./backend /app
COPY best_YOLOv8n_model.pt /app
COPY ./best_openvino_model /app/best_openvino_model
COPY requirements.txt /app

# Set working directory from now on
WORKDIR /app

# Install python packages
RUN apt-get update && apt-get install ffmpeg libsm6 libxext6 -y
RUN python -m pip cache purge
RUN python -m pip install -r requirements.txt --no-cache-dir --timeout=2000