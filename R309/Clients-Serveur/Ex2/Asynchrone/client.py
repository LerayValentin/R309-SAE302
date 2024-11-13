import socket, threading

client_connected = True

def recevoir_messages(client):
    global client_connected
    while client_connected:
        try:
            reponse = client.recv(1024).decode()
        except ConnectionResetError:
            print("Connexion perdue avec le serveur")
            break
        except ConnectionAbortedError:
            pass
        except OSError:
            exit()
        else:
            print("Réponse du serveur :", reponse)
            if reponse == 'bye':
                client_connected = False


client = socket.socket()
client.connect(('localhost', 2000))

while client_connected:
    thread_reception = threading.Thread(target=recevoir_messages, args=(client,))
    thread_reception.start()
    message = input("Entrez un message : ")
    client.send(message.encode())
    if message == 'bye' or message == 'arret':
        print("Connection coupée avec le serveur")
        client_connected = False

client.close()
