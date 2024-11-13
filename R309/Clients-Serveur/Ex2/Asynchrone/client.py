import socket
import threading

def recevoir_messages(client):
    while True:
        try:
            reponse = client.recv(1024).decode()
        except ConnectionResetError:
            print("Connexion perdue avec le serveur")
            break
        except ConnectionAbortedError:
            print("Connection coupée avec le serveur")
        except OSError:
            exit()
        else:
            if not reponse:
                break
            print("Réponse du serveur :", reponse)

def envoyer_messages(client):
    while True:
        try:
            message = input("Entrez un message : ")
        except EOFError:
            print('keyboarinterrrupt, type "bye" to quit ')
        else:
            client.send(message.encode())
            if message == 'bye' or message == 'arret':
                break

client = socket.socket()
client.connect(('localhost', 2000))

thread_reception = threading.Thread(target=recevoir_messages, args=(client,))
thread_envoi = threading.Thread(target=envoyer_messages, args=(client,))

thread_reception.start()
thread_envoi.start()

thread_envoi.join()
client.close()
