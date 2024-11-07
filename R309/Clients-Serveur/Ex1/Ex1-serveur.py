import socket

serveur = socket.socket()
serveur.bind(('localhost', 2000))
serveur.listen(1)

print("Serveur en attente de connexion...")
conn, addr = serveur.accept()
print(f"Connexion etablie avec {addr}")

message = conn.recv(1024).decode()
print("Message recu :", message)
reply = 'Message recu'
conn.send(reply.encode())

conn.close()
serveur.close()
