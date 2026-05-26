import socket

SERVER_HOST = "127.0.0.1"
SERVER_PORT = 9000
CLIENT_PORT = 9001

client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client_socket.bind(("", CLIENT_PORT))

message = "HELLO"
client_socket.sendto(message.encode(), (SERVER_HOST, SERVER_PORT))
print("Sent to server:", message)

reply, server_address = client_socket.recvfrom(2048)
print("Echo from server:", reply.decode())

client_socket.close()
