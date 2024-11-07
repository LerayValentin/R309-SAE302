import socket

serveur = socket.socket()
serveur.bind(('localhost', 2000))
serveur.listen(1)

print("Serveur en attente de connexion...")
while True:
    conn, addr = serveur.accept()
    print(f"Connexion etablie avec {addr}")

    while True:
        message = conn.recv(1024).decode()
        print("Message reçu :", message)
        
        if message == 'bye':
            print("Le client s'est deconnecte.")
            break
        elif message == 'arret':
            print("Arret du serveur...")
            serveur.close()
            exit()
        conn.send("Message recu".encode())
    
    conn.close()
    print("Connexion fermee.")