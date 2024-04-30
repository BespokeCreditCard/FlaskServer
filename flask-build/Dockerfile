FROM tiangolo/uwsgi-nginx:python3.10

# Install requirements
COPY ./requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

ENV FLASK_APP main:app

# Add demo app
COPY . /app
WORKDIR /app
CMD ["python3", "-m", "flask", "run", "--host=0.0.0.0"]