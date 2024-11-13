import socket

client = socket.socket()
client.connect(('127.0.0.1', 2000))

client.send("Hello world".encode())
reply = client.recv(1024).decode()
print("Réponse du serveur :", reply)

client.close()