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

The **server code** is responsible for generating random numbers and exposing them over a network. It is located under: `kubernetes_rbac_real_example/randomNumberServer/server.py`

#### Create the Docker Image for the Server

First, we need to create a Dockerfile for the server: `kubernetes_rbac_real_example
/randomNumberServer/Dockerfile` 

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

The **client code** connects to the server and retrieves the random numbers. It is located under: `kubernetes_rbac_real_example/randomNumberClient/client.py`

#### Create the Docker Image for the Client

Create a Dockerfile for the client: `kubernetes_rbac_real_example
/randomNumberClient/Dockerfile`

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

Once installed and your cluster set up, check the nodes in your cluster:

```bash
kind get nodes

kind-worker2
kind-control-plane
kind-worker
kind-worker3
```

### Deploying RBAC to Kubernetes

Once we've confirmed that the Docker containers work correctly, we can deploy both the server and client to a **Kubernetes cluster**. 

Create a pod file to deploy the server and client. If you wish change the image to use your own dockerhub account. E.g. if your account name is `johnmcollins`, then the image is set to `johnmcollins/random-number-server` and `johnmcollins/random-number-client`.

First, create the namespace:

```bash
kubectl create namespace random-numbers
```

#### Server

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

We need to ensure our service DNS is working correctly. We can do this by creating a pod that will run a `nslookup` command to the service.

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

Run the `nslookup` command to verify the service:

```bash
kubectl exec -ti dnsutils -n random-numbers -- nslookup random-number-service
Server:         10.96.0.10
Address:        10.96.0.10#53

Name:   random-number-service.random-numbers.svc.cluster.local
Address: 10.96.35.141
```

So we now know for sure our DNS is working correctly, and our FQDN is `random-number-service.random-numbers.svc.cluster.local`.

In the client pod, set the environment variable `RANDOM_NUMBER_SERVER` to the FQDN of the server service.

#### Client

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

Create a random number client service:

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

Deploy the client and random number client service to the cluster:

```bash
kubectl apply -f random-number-client.yaml
kubectl apply -f random-number-client-service.yaml
```

Check that all the service endpoints are created; it should not show `none`:

```bash
kubectl get ep -n random-numbers

NAME                           ENDPOINTS          AGE
random-number-client-service   10.244.2.6:3216    12s
random-number-service          10.244.1.12:3215   87s
```

### Testing the Client and Server

Connect to the host using the dnsutils pod and test the client and server:

```bash
kubectl exec -ti dnsutils -n random-numbers -- sh
```

Test the application and use `Ctrl-C` to exit:

```bash
nc random-number-client-service 3216

Enter 3 numbers min,max,cols separated by commas: 10,36,6
16      19      17      30      31      25
28      14      35      32      29      34
20      18      12      33      27      24
36      23      22      26      21      10
15      11      13
```

### Using RBAC in Kubernetes

The next step is to set up **RBAC** to allow the client to interact with the server.

Create a Service Account.
```bash
kubectl create sa random-numbers-sa -n  random-numbers
```

#### Step 1: Create a Role for Access

First, we create a **Role** that defines the permissions for accessing the server. This role grants read access to the server's resources.

For example, the role could be defined in a YAML file:

```yaml
cat <<EOF> roles.yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  namespace: random-numbers
  name: client-access-role
rules:
- apiGroups: [""]
  resources:
    - configmaps
    - services # Add other resources as needed
  verbs: 
    - get
    - list # Add other verbs as needed
EOF
```

#### Step 2: Create a RoleBinding

Now, we create a **RoleBinding** to bind the "client-access-role" to the client pod. This will grant the client the necessary permissions to interact with the server pod.

For example, the RoleBinding might look like this:

```yaml
cat <<EOF> role-binding.yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: client-access-role-binding
  namespace: random-numbers
subjects:
- kind: ServiceAccount
  name: random-numbers-sa
  namespace: random-numbers
roleRef:
  kind: Role
  name: client-access-role
  apiGroup: rbac.authorization.k8s.io
EOF
```

### Testing in Kubernetes

After deploying the server and client containers to Kubernetes, you can test the connection between them and verify that the **RoleBinding** is working. We will do this with a simple curl application.

Create the curl application:
```bash
cat <<EOF> curlapp.yaml
apiVersion: v1
kind: Pod
metadata:   
  name: curlo
  namespace: random-numbers
  labels:
    app: curlo
spec:
  serviceAccountName: random-numbers-sa
  containers:
  - name: curlo
    image: curlimages/curl
    command: ["sleep","999999"]
EOF

kubectl apply -f curlapp.yaml
```

Connect to the host using the following command
```bash
kubectl exec -it curlo -n random-numbers -- /bin/sh
```

In order to use curl with https we will need to use the certificate file `ca.crt` file and `token` in the `curl` command.

```bash
cat /var/run/secrets/kubernetes.io/serviceaccount/token > TOKEN
export TOKEN=$(cat TOKEN)
curl -k --header "Authorization: Bearer $TOKEN" --cacert /var/run/secrets/kubernetes.io/serviceaccount/ca.crt https://kubernetes.default.svc
```
For various reasons which I will let you discover, you will notice how this can be shortened to:

```bash
export CURL_CA_BUNDLE=/var/run/secrets/kubernetes.io/serviceaccount/ca.crt
curl -k --header "Authorization: Bearer $TOKEN" https://kubernetes.default.svc
```

With the following command you should be able to see the service we had created earlier

```bash
curl -k --header "Authorization: Bearer $TOKEN" https://kubernetes.default.svc/api/v1/namespaces/random-numbers/services/random-number-service
```
Result:
```bash
{
  "kind": "Service",
  "apiVersion": "v1",
  "metadata": {
    "name": "random-number-service",
    "namespace": "random-numbers",
    "uid": "504cd44b-7e10-4ea2-9ee8-a912909f6dee",
    "resourceVersion": "183093",
    "creationTimestamp": "2025-01-19T19:52:28Z",
    "managedFields": [
  ...
  "status": {
    "loadBalancer": {}
  }
```

Try to list the other pods that are running in the cluster within the same namespace using the following `curl` command. You should get a `403 Forbidden error`.

```bash
curl -k --header "Authorization: Bearer $TOKEN" https://kubernetes.default.svc/api/v1/namespaces/random-numbers/pods
```
Result
```json
{
  "kind": "Status",
  "apiVersion": "v1",
  "metadata": {},
  "status": "Failure",
  "message": "pods is forbidden: User \"system:serviceaccount:random-numbers:random-numbers-sa\" cannot list resource \"pods\" in API group \"\" in the namespace \"random-numbers\"",
  "reason": "Forbidden",
  "details": {
    "kind": "pods"
  },
  "code": 403
}
```

Great! Now we have achieved the exact level of role-based access control needed to limit access exclusively to `services` and `configmaps` within the `random-numbers` namespace.

Next, create a `ConfigMap` to store the `min`, `max`, and `table -size` values for our random number generator. These values will be used by the client pod to generate the random number table.

```bash
kubectl create configmap random-number-config --from-literal=min=1 --from-literal=max=100 --from-literal=table-size=10 -n random-numbers
```

Here is the yaml file version of the same command:
```yaml
cat <<EOF> random-number-configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: random-number-config
  namespace: random-numbers
data:
  min: "1"
  max: "100"
  table-size: "10"
  table-name: "random-numbers"
EOF

kubectl apply -f random-number-configmap.yaml
```
### Python Kubernetes API Client

We need to modify the client pod to use the Kubernetes API to get the `configmap` values and use them to generate the random number table.

We will use the Kubernetes API client for Python to get the configmap values.

The source code can be found here: `kubernetes_rbac_real_example/randomNumberClientCM/client-cm.py`

We will need to add the kubernetes library to our Docker image. Use `pip` to install the Kubernetes API client for Python in your Dockerfile ( note we have already done this for you ).
```bash
pip install kubernetes
```

Here is the code required to get the configmap values:
```python
import os
from kubernetes import client, config
def get_configmap_values():
    config.load_incluster_config()
    v1 = client.CoreV1Api()
    configmap = v1.read_namespaced_config_map(name="random-number-config", namespace="random-numbers")
    min_value = int(configmap.data["min"])
    max_value = int(configmap.data["max"])
    table_size = int(configmap.data["table-size"])
    return min_value, max_value, table_size
```

Build a new docker image called `{your-username}/random-number-client-cm` and push it to docker hub.

```bash
docker build -t {your-username}/random-number-client-cm .
docker push {your-username}/random-number-client-cm
```


Lets double check we have our service account added the client pod definition and the lastest docker image for the client pod. Remember, the service account is used to restrict access to the Kubernetes API using RBAC.

```bash
apiVersion: v1
kind: Pod
metadata:
  labels:
    app: random-number-client
  name: random-number-client
  namespace: random-numbers
spec:
  serviceAccountName: random-numbers-sa
  containers:
  - name: random-number-client
    image: {your-docker-username}/random-number-client-cm:latest
    ports:
    - containerPort: 3216
    env:
    - name: RANDOM_SERVER
      value: "random-number-service.random-numbers.svc.cluster.local"
```

```bash
kubectl delete -f random-number-client.yaml
kubectl apply -f random-number-client.yaml
```

If everything is set up correctly, the client should be able to access the server and receive the random number table, just like it did in the Docker environment but can't do very much else. Let's test it out:

```bash
kubectl exec -ti dnsutils -n random-numbers -- sh

/ # nc random-number-client-service 3216

Press [Enter] to get a new set of values using the kubernetes config map: 
Will send these values to server: 1,100,10
Waiting for server response...
74      80      40      26      17      72      87      38      64      79
97      96      63      86      7       58      75      52      76      32
47      29      5       83      68      90      60      100     16      70
84      9       44      37      48      49      98      81      27      54
45      61      51      25      43      57      65      89      92      19
22      24      55      28      53      15      13      8       10      39
20      77      31      93      91      12      62      94      34      42
35      1       67      85      78      59      14      99      11      33
21      30      95      2       6       82      4       3       56      66
50      69      18      23      46      71      36      88      41      73

Press [Enter] to get a new set of values using the kubernetes config map:

```
Now try changing the `min`, `max` and `table-size` values in the config map and see if the client can pick up the new values.

```bash
apiVersion: v1
kind: ConfigMap
metadata:
  name: random-number-config
  namespace: random-numbers
data:
  min: "64"
  max: "256"
  table-size: "8"
  table-name: "random-numbers"
...
```
Save the file apply the changes.
```bash
kubectl apply -f random-number-configmap.yaml
```
Visit the window where you are running the dnsutils pod and hit enter again in the terminal. This should now fetch a new table using the updated `min`,`max` and `table-size` values. 

```bash
Press [Enter] to get a new set of values using the kubernetes config map: 
Will send these values to server: 64,256,8
Waiting for server response...
219     195     91      88      104     93      134     144
246     131     241     239     128     210     190     114
163     183     191     161     115     145     160     70
136     218     171     67      98      237     248     256
227     173     80      202     206     71      129     126
249     154     245     216     193     204     92      66
75      169     106     189     155     185     238     179
103     230     99      221     149     137     152     138
117     174     100     247     215     170     105     68
120     74      180     141     231     186     139     250
79      122     209     121     127     123     83      157
94      235     199     211     201     125     188     95
229     205     220     198     147     236     217     176
97      167     213     234     203     225     84      172
208     142     254     150     175     148     87      228
158     253     135     64      242     81      233     212
133     72      118     73      243     143     226     159
146     140     178     77      124     151     112     109
164     184     251     153     96      197     65      240
78      132     166     252     165     194     102     244
86      187     116     232     222     196     110     111
119     90      168     255     101     76      82      85
162     89      108     69      223     200     214     182
207     192     113     177     130     156     107     181
224
```
---

### Conclusion

In this article, we've walked through a real-world example of using **RBAC** in a Kubernetes environment. We demonstrated how to set up roles and RoleBindings to control access between two applications—one acting as a server and the other as a client. By building the applications with **Docker**, deploying them to Kubernetes, and using RBAC, you now have a solid understanding of how to implement access control in a Kubernetes cluster.

Remember, RBAC is a powerful feature that helps you ensure that users and services in your cluster have the appropriate permissions based on their roles. With RBAC, you can implement fine-grained access control to safeguard your resources.

---
