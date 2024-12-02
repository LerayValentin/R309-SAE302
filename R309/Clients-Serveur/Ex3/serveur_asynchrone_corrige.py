import socket
import threading

clients = []

def gerer_client(client_socket, adresse):
    while True:
        try:
            message = client_socket.recv(4200).decode('utf-8')
            if message == "bye":
                print(f"{adresse} a quitté la discussion.")
                clients.remove(client_socket)
                client_socket.close()
                break
            elif message == "arret":
                print("Arrêt du serveur.")
                for client in clients:
                    client.send("Le serveur est arrêté.".encode('utf-8'))
                    client.close()
                serveur_socket.close()
                exit()
            else:
                print(f"Message reçu de {adresse}: {message}")
                for client in clients:
                    if client != client_socket:
                        client.send(f"De {adresse}: {message}".encode('utf-8'))
        except:
            clients.remove(client_socket)
            client_socket.close()
            break

def envoyer_message_serveur():
    while True:
        message = input("Serveur: ")
        if message == "arret":
            print("Arrêt du serveur.")
            for client in clients:
                client.send("Le serveur est arrêté.".encode('utf-8'))
                client.close()
            serveur_socket.close()
            exit()
        else:
            for client in clients:
                client.send(f"Serveur: {message}".encode('utf-8'))

serveur_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serveur_socket.bind(('localhost', 4200))
serveur_socket.listen(5)
print("Serveur en attente de connexion...")

thread_serveur = threading.Thread(target=envoyer_message_serveur)
thread_serveur.start()

while True:
    client_socket, adresse = serveur_socket.accept()
    clients.append(client_socket)
    print(f"Nouvelle connexion de {adresse}")
    thread = threading.Thread(target=gerer_client, args=(client_socket, adresse))
    thread.start()