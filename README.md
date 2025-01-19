# RBAC in Kubernetes Real Example

In this articler we will describe how to use RBAC in Kubermnetes with a real example.
Many of the examples you will find on line seeme to all be saying the same thing but with any real world example it is not always clear how to apply it. So we will use a real world example to show how to apply RBAC in Kubernetes.

## What is RBAC

RBAC is a method of regulating access to computer or network resources based on the roles of individual users within an organization. It is a policy-neutral access-control mechanism defined around roles and privileges. The components of RBAC such as role-permissions, user-role and role-role relationships make it simple to perform user assignments (who can do what).

## What is a Role

A role is a collection of permissions. A role can be assigned to a user or a group of users. A role can also be assigned to another role. This is useful for creating a hierarchy of roles. For example, a user can be assigned a role of "admin" which has the permission to create, read, update and delete resources. The user can also be assigned a role of "developer" which has the permission to create, read and update resources. The user can also be assigned a role of "viewer" which has the permission to read resources.

## What is a RoleBinding

A RoleBinding is a binding between a role and a user or a group of users. A RoleBinding can be created to bind a role to a user or a group of users. A RoleBinding can also be created to bind a role to another role. This is useful for creating a hierarchy of roles. For example, a user can be assigned a role of "admin" which has the permission to create, read, update and delete resources. The user can also be assigned a role of "developer" which has the permission to create, read and update resources. The user can also be assigned a role of "viewer" which has the permission to read resources.

So here we have 2 applications a server and a client. Both writen in Python and easily to follow.
The server will produce a table of random numbers and the client will consume it.

We will then build these into Docker images.

Once we have our images we can te deploy them to a Kubernetes cluster.
We will then create a RoleBinding to allow the client to access the server.

Once we have build the images we can then test they work in DOCKER and then in KUBERNETES.

## Prerequisites    
You will need to have Docker installed on your machine.
You will need to have Kubernetes installed on your machine.
You will need to have Python installed on your machine.
You will need to have pip installed on your machine.
You will need to have virtualenv installed on your machine.
You will need to have kubectl installed on your machine.
You will need to have minikube installed on your machine.

## Server Code
```python
# Create a server that generates random numbers from an http server

import socket
import requests
import certifi

min = 1
max = 20
cols = 5

# Create a socket object
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Get local machine name
host = socket.gethostname()
port = 3215

# Bind to the port
s.bind((host, port))

# Now wait for client connection.
s.listen(5)
while True:
    c, addr = s.accept()
    print('Got connection from', addr)

    # make the url string above use the variables min, max, cols
    url = "https://www.random.org/sequences/?min={}&max={}&col={}&format=plain&rnd=new".format(str(min), str(max), str(cols) )

    # read the https url with ssl verify on
    f = requests.get(url, certifi.where())
    out = f.text

    # Convert string out to bytes
    out = out.encode('utf-8')

    # Send to the client
    c.send( out )
```

Build the Docker image
Create a file called Dockerfile with the following content:
```dockerfile
FROM python:3.7
COPY . /app
WORKDIR /app
CMD ["python", "server.py"]
```

Build the Docker image
```bash
docker build -t random-number-server .
```

## Client Code

```python
# Client
import socket

# Create a socket object
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Get local machine name
host = socket.gethostname()
port = 3215

# Connect to the server
s.connect((host, port))

# Receive the random number from the server
print(s.recv(1024).decode())

# Close the connection
s.close()
```

Build the Docker image
Create a file called Dockerfile with the following content:

```dockerfile
FROM python:3.7
COPY . /app
WORKDIR /app
CMD ["python", "client.py"]
```

Build the Docker image
```bash
docker build -t random-number-client .
```

## Running the Docker Containers

Run the server container
```bash
docker run -it -d --network=host --name random-number-server -p 3215:3215 random-number-server
```

Run the client container
```bash
docker run -it --network=host --name random-number-client random-number-client
```

You should see the random number printed in the client container's output as below 

```pre
18	2	1	10	9
14	11	8	17	7
13	12	3	15	20
5	6	4	16	19
```

