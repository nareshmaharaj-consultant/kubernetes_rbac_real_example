FROM python:3.7
COPY . /app
WORKDIR /app

# Use RUN to install dependencies
RUN pip install kubernetes

CMD ["python", "client-cm.py"]
