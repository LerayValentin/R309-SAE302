import socket

client_connected = True
serveur = socket.socket()
serveur.bind(('localhost', 2000))
serveur.listen(1)

while True:
    print("Serveur en attente de connexion...")
    conn, addr = serveur.accept()
    client_connected = True
    print(f"Connexion etablie avec {addr}")

    while client_connected:
        message = conn.recv(1024).decode()
        print("Message reçu :", message)
        conn.send("Message recu".encode())

        if message == 'bye':
            print("Le client s'est deconnecte.")
            client_connected = False
        elif message == 'arret':
            print("Arret du serveur...")
            serveur.close()
            exit()
    
    conn.close()
    print("Connexion fermee.")