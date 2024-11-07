import socket

client = socket.socket()
client.connect(('localhost', 2000))

while True:
    message = input("Entrez un message : ")
    client.send(message.encode())
    if message.lower() in ['bye', 'arret']:
        break
    reponse = client.recv(1024).decode()
    print("Réponse du serveur :", reponse)

client.close()
