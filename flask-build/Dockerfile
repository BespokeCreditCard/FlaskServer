FROM tiangolo/uwsgi-nginx:python3.10

# Install requirements
COPY ./flask-build/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

ENV FLASK_APP main:app

# Add demo app
COPY . /app
WORKDIR /app/flask-build/
CMD ["python3", "main.py"]