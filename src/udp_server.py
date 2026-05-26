import socket

SERVER_PORT = 9000

server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind(("", SERVER_PORT))

print("Server is running on port", SERVER_PORT)

while True:
    message, client_address = server_socket.recvfrom(2048)
    print("Received from client:", message.decode())
    server_socket.sendto(message, client_address)
    print("Echoed message back to", client_address)
