# Implementing RBAC in Kubernetes: A Real-World Example

In this article, we'll dive into how to implement **Role-Based Access Control (RBAC)** in Kubernetes through a practical, real-world example. While many tutorials cover RBAC concepts, they often remain abstract or overly simplified. By walking through an actual use case, you'll gain a better understanding of how to apply RBAC effectively in a Kubernetes cluster.

## What is RBAC?

RBAC stands for **Role-Based Access Control**. It's a method for regulating access to resources in a system based on the roles of individual users within an organization. Essentially, RBAC is a policy-neutral access control mechanism that assigns permissions to users according to their roles. The key components of RBAC in Kubernetes include:

- **Roles**: Define what actions are allowed on which resources.
- **RoleBindings**: Link roles to users, granting them the associated permissions.
- **ServiceAccounts**: Represent identities for processes running inside pods.

RBAC simplifies user assignments and ensures that access control is clear, consistent, and manageable.

## What is a Role?

In Kubernetes, a **Role** is a collection of permissions that define what actions are allowed on certain resources. Roles can be applied to users, groups, or even other roles (creating hierarchies). 

For example:
- An "Admin" role might have permissions to **create, read, update, and delete** resources.
- A "Developer" role might only have permissions to **create, read, and update** resources.
- A "Viewer" role might only have permissions to **read** resources.

Roles are a key part of RBAC as they encapsulate the actions users or processes can perform within Kubernetes.

## What is a RoleBinding?

A **RoleBinding** is the mechanism that binds a Role to a user, a group of users, or even other roles. A RoleBinding effectively grants the permissions defined in a Role to whoever is bound to it. 

For example:
- You can bind the "Admin" role to a user, which grants them full access to Kubernetes resources.
- You can also create a RoleBinding that binds the "Viewer" role to a group of users, allowing them to only read the resources.

RoleBindings are essential for controlling access to Kubernetes resources, ensuring that users have the correct permissions according to their roles.

## Real-World Example: A Python Server and Client in Kubernetes

In this example, we will implement RBAC in a Kubernetes environment to control access between two applications: a **server** and a **client**.

- **Server**: This application generates a table of random numbers.
- **Client**: This application consumes the random number data from the server.

We will containerize both applications using **Docker** and then deploy them to a **Kubernetes cluster**. Finally, we'll create a **RoleBinding** to allow the client to access the server.

### Prerequisites

Before we begin, ensure you have the following installed on your machine:
- `Docker` (e.g., Docker Desktop)
- `Kubernetes` (e.g., Minikube, kind or a local Kubernetes setup)
- `Python` (preferably version 3.x)
- `pip` (Python package manager)
- `virtualenv` (for managing Python environments)
- `kubectl` (Kubernetes command-line tool)
- `netcat` (for network testing)

### Server Code

The **server code** is responsible for generating random numbers and exposing them over a network. It is located under:

```bash
kubernetes_rbac_real_example/randomNumberServer/server.py
```

#### Create the Docker Image for the Server

First, we need to create a Dockerfile for the server:

```dockerfile
FROM python:3.7
COPY . /app
WORKDIR /app
CMD ["python", "server.py"]
```

To build the Docker image:

```bash
export dockerhub_username=<your_dockerhub_username>
docker build -t ${dockerhub_username}/random-number-server .
docker push ${dockerhub_username}/random-number-server
```

### Client Code

The **client code** connects to the server and retrieves the random numbers. It is located under:

```bash
kubernetes_rbac_real_example/randomNumberClient/client.py
```

#### Create the Docker Image for the Client

Create a Dockerfile for the client:

```dockerfile
FROM python:3.7
COPY . /app
WORKDIR /app
CMD ["python", "client.py"]
```

To build the Docker image:

```bash
export dockerhub_username=<your_dockerhub_username>
docker build -t ${dockerhub_username}/random-number-client .
docker push ${dockerhub_username}/random-number-client
```

### Running the Docker Containers

Next, we'll set up a **Docker network** to allow communication between the server and client containers:

```bash
docker network create -d bridge random-net
```

Now, run the **server container**:

```bash
docker run -it -d --name random-number-server -p 3215 --network=random-net --hostname random01 random-number-server
```

Run the **client container**:

```bash
docker run -it -d --name random-number-client -p 3216:3216 --network=random-net -e RANDOM_SERVER=random01 --hostname=random02 random-number-client
```

### Testing the Setup with `netcat`

In a new shell, use **netcat** to connect to the client container's port and view the random numbers it receives:

```bash
nc localhost 3216
```

You'll be prompted to enter parameters for the number generation. Here's an example of output you should see:

```pre
Enter 3 numbers min,max,cols separated by commas: 1,900,12

565    636    362    538    483    103    898    188    81    432    245    519
120    644    866    487    407    534    156    870    630    418    581    231
174    43     675    9      380    60     555    127    505    471    764    191
...
```

### Kubernetes Environment using Kind

Visit the [Kind documentation](https://kind.sigs.k8s.io/docs/user/quick-start/) for detailed instructions on setting up a Kubernetes cluster using Kind.

Once installed and your cluster set up check the nodes in your cluster:
```
kind get nodes

kind-worker2
kind-control-plane
kind-worker
kind-worker3
```

Create a pod file to deploy the server and client.

First Create the namespace:
```bash
kubectl create namespace random-numbers
```
Server:

```bash
cat <<EOF> random-number-server.yaml
apiVersion: v1
kind: Pod
metadata:
  labels:
    app: random-number-server
  name: random-number-server
  namespace: random-numbers
spec:
  containers:
  - name: random-number-server
    image: contactnkm/random-number-server:latest
    ports:
    - containerPort: 3215
EOF
```

Create the service for this pod:
```bash
cat <<EOF> random-number-service.yaml
apiVersion: v1
kind: Service
metadata:
  name: random-number-service
  namespace: random-numbers
spec:
  selector:
    app: random-number-server
  ports:
    - protocol: TCP
      port: 3215
      targetPort: 3215
EOF
```

Run the following commands to deploy the random number server and random number service:

```bash
kubectl apply -f random-number-server.yaml
kubectl apply -f random-number-service.yaml
```

We need to be able ti ensure our service DNS is working correctly. We can do this by creating a pod that will run a nslookup command to the service.

```bash
cat <<EOF> dnsutils.yaml
apiVersion: v1
kind: Pod
metadata:
  name: dnsutils
  namespace: default
spec:
  containers:
  - name: dnsutils
    image: gcr.io/kubernetes-e2e-test-images/dnsutils:1.3
    command:
      - sleep
      - "3600"
    imagePullPolicy: IfNotPresent
  restartPolicy: Always
EOF
```

```bash
kubectl apply -f dnsutils.yaml
```

Run the nslookup command to the verify the service:
```bash
kubectl exec -ti dnsutils -n random-numbers -- n
slookup random-number-service
Server:         10.96.0.10
Address:        10.96.0.10#53

Name:   random-number-service.random-numbers.svc.cluster.local
Address: 10.96.35.141
```

So we now know for sure our DNS is working correctly and our FQDN is `random-number-service.random-numbers.svc.cluster.local`

In the client pod set the environment variable `RANDOM_NUMBER_SERVER` to the FQDN of the server service.

Client:

```bash
cat <<EOF> random-number-client.yaml
apiVersion: v1
kind: Pod
metadata:
  labels:
    app: random-number-client
  name: random-number-client
  namespace: random-numbers
spec:
  containers:
  - name: random-number-client
    image: contactnkm/random-number-client:latest
    ports:
    - containerPort: 3216
    env:
    - name: RANDOM_SERVER
      value: "random-number-service.random-numbers.svc.cluster.local"
EOF
```

Create a random number client service
```bash
cat <<EOF> random-number-client-service.yaml
apiVersion: v1
kind: Service
metadata:
  name: random-number-client-service
  namespace: random-numbers
spec:
  selector:
    app: random-number-client
  ports:
    - protocol: TCP
      port: 3216
      targetPort: 3216
EOF
```

Deploy the and client and random number client and random number service to the cluster:

```bash
kubectl apply -f random-number-client.yaml
```

Check that all the service endpoints are created, it should not show `none`.
```bash
kubectl get ep -n random-numbers

NAME                           ENDPOINTS          AGE
random-number-client-service   10.244.2.6:3216    12s
random-number-service          10.244.1.12:3215   87s
```

### Testing the Client and Server
Connect to the host using the dns utils pod and test the client and server.
```bash
kubectl exec -ti dnsutils -n random-numbers -- sh
```
Test the application and use ctrl-c to exit
```bash
nc random-number-client-service 3216

Enter 3 numbers min,max,cols separated by commas: 10,36,6
16      19      17      30      31      25
28      14      35      32      29      34
20      18      12      33      27      24
36      23      22      26      21      10
15      11      13
```

- Work in progress from here onwards.

### Deploying to Kubernetes

Once we've confirmed that the Docker containers work correctly, we can deploy both the server and client to a **Kubernetes cluster**. The next step is to set up **RBAC** to allow the client to interact with the server.

#### Step 1: Create a Role for Access

First, we create a **Role** that defines the permissions for accessing the server. This role grants read access to the server's resources.

For example, the role could be defined in a YAML file:

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  namespace: default
  name: client-access-role
rules:
- apiGroups: [""]
  resources: ["pods"]
  verbs: ["get", "list"]
```

#### Step 2: Create a RoleBinding

Now, we create a **RoleBinding** to bind the "client-access-role" to the client pod. This will grant the client the necessary permissions to interact with the server pod.

For example, the RoleBinding might look like this:

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: client-rolebinding
  namespace: default
subjects:
- kind: ServiceAccount
  name: default
  namespace: default
roleRef:
  kind: Role
  name: client-access-role
  apiGroup: rbac.authorization.k8s.io
```

### Testing in Kubernetes

After deploying the server and client containers to Kubernetes, you can test the connection between them and verify that the **RoleBinding** is working. 

If everything is set up correctly, the client should be able to access the server and receive the random number table, just like it did in the Docker environment.

---

### Conclusion

In this article, we've walked through a real-world example of using **RBAC** in a Kubernetes environment. We demonstrated how to set up roles and RoleBindings to control access between two applications—one acting as a server and the other as a client. By building the applications with **Docker**, deploying them to Kubernetes, and using RBAC, you now have a solid understanding of how to implement access control in a Kubernetes cluster.

Remember, RBAC is a powerful feature that helps you ensure that users and services in your cluster have the appropriate permissions based on their roles. With RBAC, you can implement fine-grained access control to safeguard your resources.

---

Let me know if you need any further modifications or more details!