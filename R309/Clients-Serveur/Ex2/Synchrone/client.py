import socket
client_connected = True
client = socket.socket()
client.connect(('localhost', 2000))

while client_connected:
    message = input("Entrez un message : ")
    client.send(message.encode())
    if message == 'bye' or message == 'arret':
        client_connected = False
    reponse = client.recv(1024).decode()
    print("Réponse du serveur :", reponse)

client.close()
