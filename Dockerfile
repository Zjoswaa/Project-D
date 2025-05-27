FROM python:3.9-slim  # More stable than 3.13.3

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "-u", "app/chadbot_sigma_v1.py"]  # Explicit path