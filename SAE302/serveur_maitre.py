import socket
import threading

etat_serveur = True
esclaves_actifs = []

def gerer_client(conn, addr):
    global etat_serveur
    print(f"Client connecté : {addr}")
    while etat_serveur:
        try:
            script = conn.recv(1024).decode()
            if not script:
                print(f"Client {addr} déconnecté.")
                etat_serveur = False
            result = redistribuer_script(script)
            conn.send(result.encode())
        except ConnectionResetError:
            print(f"Connexion perdue avec {addr}.")
            etat_serveur = False
        except Exception as e:
            print(f"Erreur avec le client {addr}: {e}")
            etat_serveur = False
    conn.close()
    print(f"Connexion fermée avec {addr}")

def gerer_esclave(conn, addr):
    global etat_serveur
    print(f"Esclave connecté : {addr}")
    esclaves_actifs.append((conn, addr))
    try:
        while etat_serveur:
            message = conn.recv(1024).decode()
            if not message:
                print(f"Esclave déconnecté : {addr}")
                break
    except Exception as e:
        print(f"Erreur avec l'esclave {addr}: {e}")
    finally:
        esclaves_actifs.remove((conn, addr))
        conn.close()

def redistribuer_script(script):
    if not esclaves_actifs:
        return "Erreur : Aucun esclave disponible."
    for esclave_conn, esclave_addr in esclaves_actifs:
        try:
            print("envoi au slave...")
            esclave_conn.sendall(script.encode())
            reponse = esclave_conn.recv(1024).decode()
            print(f"réponse : {reponse}")
            if reponse:
                return reponse
        except Exception as e:
            print(f"Erreur avec l'esclave {esclave_addr}: {e}")
            continue
    return "Erreur : Aucun esclave n'a répondu."


def accepter_slave():
    print("En attente de nouveaux esclaves...")
    while True:
        try:
            slave_conn, slave_addr = serveur_esclaves.accept()
            esclaves_actifs.append((slave_conn, slave_addr))
            print(f"Esclave connecté depuis {slave_addr}. Total d'esclaves : {len(esclaves_actifs)}")
        except Exception as e:
            print(f"Erreur lors de l'acceptation d'un esclave : {e}")
            break



if __name__ == "__main__":
    PORT_CLIENTS = 4200  # Port pour les clients
    PORT_ESCLAVES = 4301  # Port pour les esclaves

    serveur_clients = socket.socket()
    serveur_esclaves = socket.socket()

    try:
        serveur_esclaves.bind(('0.0.0.0', PORT_ESCLAVES))
        serveur_esclaves.listen(5)
        print(f"Serveur maître (esclaves) en attente sur le port {PORT_ESCLAVES}...")
        thread_esclaves = threading.Thread(target=accepter_esclaves)
        thread_esclaves.start()

        serveur_clients.bind(('0.0.0.0', PORT_CLIENTS))
        serveur_clients.listen(5)
        print(f"Serveur maître (clients) en attente sur le port {PORT_CLIENTS}...")
        while etat_serveur:
            try:
                conn_client, addr_client = serveur_clients.accept()
                print(f"Nouveau client connecté : {addr_client}")
                thread_client = threading.Thread(target=gerer_client, args=(conn_client, addr_client))
                thread_client.start()
            except KeyboardInterrupt:
                print("\nArrêt du serveur...")
                etat_serveur = False
                break

    except Exception as e:
        print(f"Erreur au démarrage du serveur : {e}")
    finally:
        serveur_clients.close()
        serveur_esclaves.close()
