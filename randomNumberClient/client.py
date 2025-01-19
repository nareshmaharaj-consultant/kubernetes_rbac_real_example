# Client
import socket
import os

def is_socket_connected(sock):
    try:
        sock.send(b'')
    except socket.error:
        return False
    return True

# Should never get back to here unless there is an error
while True:
    # Create a socket object
    clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Get Environment variable
    random_number_server_host = os.getenv('RANDOM_SERVER')
    if random_number_server_host is None:
        print( "Environment variable RANDOM_SERVER is not set")
        exit(1)

    # Get local machine name
    host = socket.gethostname()
    port = 3216

    # Bind to the port
    clientSocket.bind(( host, port) )
    connection = None
    randomNumberServerSocket = None

    try:
        # Now wait for client connection.
        clientSocket.listen(5)
        connection, addr = clientSocket.accept()
        print('Got connection from', addr)
        
        while True:        

            # Check if the client is still connected
            if is_socket_connected(connection) == False:
                print("Connection closed - waiting for new connections")
                clientSocket.listen(5)
                connection, addr = clientSocket.accept()
                print('Established new connection from', addr)
            else:
                print("Connection is open")

            # Establish connection with client.
            connection.send('\nEnter 3 numbers min,max,cols separated by commas: '.encode())
            data = connection.recv(1024).decode()

            # Create socket object connect to the server for random numbers
            # If no data from rnaom number server but random but is connected
            # assume client not sending any requests i.e. client
            # is not asking for random numbers. Check if the client is still connected
            # with is_socket_connected(connection) == False above.
            try:           
                randomNumberServerSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)        
                randomNumberServerSocket.connect((random_number_server_host, 3215))
                randomNumberServerSocket.send(data.encode())
                randomNumberServerSocket.settimeout(0.5)
                data = randomNumberServerSocket.recv(1024).decode()
            except socket.timeout:
                print("ERROR-1-Timeout error")
                randomNumberServerSocket.close()
                continue
            except socket.error:
                print("ERROR-2-Socket error")
                randomNumberServerSocket.close()
                continue
            except:
                print("ERROR-3-Some error occured")
                randomNumberServerSocket.close()
                continue

            # Send the results back to the client
            connection.send(data.encode())
            randomNumberServerSocket.close()

    except KeyboardInterrupt:
        print("ERROR-4-Closing socket")
        clientSocket.close()
        if connection is not None:
            connection.close()
        if randomNumberServerSocket is not None:
            randomNumberServerSocket.close()    
    except:
        print("ERROR-5-Some error occured")

    if connection is not None:
        connection.close()
    if randomNumberServerSocket is not None:
        randomNumberServerSocket.close()
    if clientSocket is not None:
        clientSocket.close()


## Build docker image for the client
# docker build -t random-number-client .

## Run the client container
# docker run -it --network=host random-number-client