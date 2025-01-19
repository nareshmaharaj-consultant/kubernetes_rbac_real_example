# Create a docker image to run the above server
# Create a Dockerfile
FROM python:3.7
COPY . /app
WORKDIR /app
RUN pip install requests certifi
CMD ["python", "server.py"]
