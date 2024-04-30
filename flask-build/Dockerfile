FROM python:3.10-slim

# Install requirements
COPY ./flask-build/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

ENV FLASK_APP main:app

# Add demo app
COPY . /app
WORKDIR /app
CMD ["python3", "main.py"]