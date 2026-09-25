FROM python:3.13-slim
WORKDIR /app
COPY runtime/ /app/
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
CMD ["python", "server.py"]
