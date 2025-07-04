import socket
import threading
etat_serveur = True

def gerer_client(conn, addr):
    global etat_serveur
    global client_connected
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
            
        except ConnectionResetError:
            print(f"connexion perdue avec {addr}")
            break

    conn.close()
    print(f"Connexion fermee avec {addr}")

def envoi_message(conn, addr):
    global client_connected
    while client_connected:
        message = input('entrez un message : ')
        if message == 'bye':
            client_connected = False
        try:
            conn.send(message.encode())
        except OSError:
            pass

serveur = socket.socket()
serveur.bind(('0.0.0.0', 2000))
serveur.listen(5)

print("en attente de connexion...")

while etat_serveur:
    try:
        conn, addr = serveur.accept()
        client_connected = True
    except OSError:
        pass
    else:
        thread_envoi = threading.Thread(target=envoi_message, args=(conn, addr))
        thread = threading.Thread(target=gerer_client, args=(conn, addr))
        thread.start()
        thread_envoi.start()

