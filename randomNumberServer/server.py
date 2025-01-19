# Create a server that generates random numbers from an http server
# Makes client happy

import socket
import requests
import certifi

def sendErr(connecton, err):
    connecton.send( err.encode('utf-8') )
    print(err)
    return

# Create a socket object
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Get local machine name
host = socket.gethostname()
port = 3215

# Bind to the port
client_socket.bind((host, port))

# Now wait for client connection.
try:
    while True:
        client_socket.listen(5)
        connecton, addr = client_socket.accept()

        # Print the address of the client
        print('Got connection from', addr)

        # Receive the data from the client
        data = connecton.recv(1024).decode().strip()
        print("Data received: {}".format(data))

        # Check if data is empty
        if  len(data) == 0 or data == "" or data == None:
            err = "No data received"
            sendErr(connecton, err)        
            continue
        # Check data is in the format min,max,cols
        if not "," in data:
            err = "Data not in correct format no comma"
            sendErr(connecton, err)        
            continue
        # Check data is in the format min,max,cols
        if len(data.split(",")) != 3:
            err = "Data not in correct format not 3 values"
            sendErr(connecton, err)        
            continue
        # Check data is in the format min,max,cols
        if not data.split(",")[0].isdigit() or not data.split(",")[1].isdigit() or not data.split(",")[2].isdigit():
            err = "Data not in correct format not digits"
            sendErr(connecton, err)        
            continue
        # Check data is in the format min,max,cols
        if int(data.split(",")[0]) > int(data.split(",")[1]):
            err = "Data not in correct format min > max"
            sendErr(connecton, err)        
            continue
        # Check data is in the format min,max,cols
        if int(data.split(",")[2]) < 1:
            err = "Data not in correct format cols < 1"
            sendErr(connecton, err)        
            continue

        # parse the data string to get the min, max, cols
        min = int(data.split(",")[0])
        max = int(data.split(",")[1])
        cols = int(data.split(",")[2])

        # make the url string above use the variables min, max, cols
        address = "https://www.random.org/sequences/?min={}&max={}&col={}&format=plain&rnd=new"
        url = address.format(str(min), str(max), str(cols) )

        # read the https url with ssl verify on where() will use root certs
        resposne = requests.get(url, certifi.where())
        out = resposne.text

        # Convert string out to bytes
        out = out.encode('utf-8')

        # Send to the client
        connecton.send( out )
except KeyboardInterrupt:
    print("\nClosing socket")
    client_socket.close()
    connecton.close()
    exit()

# Close the socket
client_socket.close()
c.close()

# Create a docker image to run the above server

## Build the docker image
# docker build -t random-number-server .

## Run the docker image
# docker run -it -d --network=host --name random-number-server -p 3215:3215 random-number-server