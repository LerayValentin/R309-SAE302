import socket
import threading
etat_serveur = True

def gerer_client(conn, addr):
    global etat_serveur
    client_connected = True
    print(f"Connexion etablie avec {addr}")
    while client_connected:
        try:
            message = conn.recv(1024).decode()
            print(f"Message reçu de {addr} : {message}")

            if message == 'bye':
                print(f"Le client {addr} s'est deconnecte.")
                client_connected = False
            elif message == 'arret':
                print("Arret du serveur...")
                etat_serveur = False
                serveur.close()
                exit()
            
            conn.send("Message reçu".encode())
        except ConnectionResetError:
            print(f"connexion perdue avec {addr}")
            break

    conn.close()
    print(f"Connexion fermee avec {addr}")

serveur = socket.socket()
serveur.bind(('0.0.0.0', 2000))
serveur.listen(5)

print("en attente de connexion...")

while etat_serveur:
    try:
        conn, addr = serveur.accept()
    except OSError:
        pass
    else:
        thread = threading.Thread(target=gerer_client, args=(conn, addr))
        thread.start()

