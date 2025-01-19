# Client
import socket


# Create a socket object
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Get local machine name
host = socket.gethostname()
port = 3216

# Bind to the port
clientSocket = socket.bind((host, port))

try:
    # Now wait for client connection.
    clientSocket.listen(5)
    connection, addr = clientSocket.accept()
    print('Got connection from', addr)
    
    while True:        
        # Establish connection with client.
        connection.send('\nEnter 3 numbers min,max,cols separated by commas: '.encode())
        data = connection.recv(1024).decode()

        # Create a socket object to connect to the server for random numbers
        randomNumberServerSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        randomNumberServerSocket.connect((host, 3215))
        randomNumberServerSocket.send(data.encode())
        data = randomNumberServerSocket.recv(1024).decode()

        # Send the results back to the client
        connection.send(data.encode())
        randomNumberServerSocket.close()

except KeyboardInterrupt:
    print("\nClosing socket")
    clientSocket.close()
    connection.close()
    randomNumberServerSocket.close()
    exit()

connection.close()
clientSocket.close()
randomNumberServerSocket.close()

## Build docker image for the client
# docker build -t random-number-client .

## Run the client container
# docker run -it --network=host random-number-client

