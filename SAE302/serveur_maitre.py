import socket, threading, argparse

esclaves_actifs = []

def gerer_client(conn, addr):
    print(f"Client connecté : {addr}")
    while True:
        try:
            script = conn.recv(1024).decode()
            if not script:
                print(f"Client {addr} déconnecté.")
                break
            result = redistribuer_script(script)
            conn.send(result.encode())
        except ConnectionResetError:
            print(f"Connexion perdue avec {addr}.")
            break
        except Exception as e:
            print(f"Erreur avec le client {addr}: {e}")
            break
    conn.close()
    print(f"Connexion fermée avec {addr}")

def redistribuer_script(script):
    if not esclaves_actifs:
        return "Erreur : Aucun esclave disponible."
    for esclave_conn, esclave_addr in esclaves_actifs[:]:
        try:
            print("Envoi au slave...")
            esclave_conn.sendall(script.encode())
            reponse = esclave_conn.recv(1024).decode()
            print(f"Réponse : {reponse}")
            if reponse:
                return reponse
        except Exception as e:
            print(f"Erreur avec l'esclave {esclave_addr}: {e}")
            esclaves_actifs.remove((esclave_conn, esclave_addr))
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
    parser = argparse.ArgumentParser(description="Serveur maître pour clients et esclaves.")
    parser.add_argument("--pc",type=int,default=4200,help="Port utilisé pour les connexions clients (par défaut : 4200).")
    parser.add_argument("--pe",type=int,default=4300,help="Port utilisé pour les connexions esclaves (par défaut : 4301).")
    args = parser.parse_args()

    PORT_CLIENTS = args.pc
    PORT_ESCLAVES = args.pe

    serveur_clients = socket.socket()
    serveur_esclaves = socket.socket()

    try:
        serveur_esclaves.bind(('0.0.0.0', PORT_ESCLAVES))
        serveur_esclaves.listen(5)
        print(f"Serveur maître (esclaves) en attente sur le port {PORT_ESCLAVES}...")
        thread_esclaves = threading.Thread(target=accepter_slave)
        thread_esclaves.start()

        serveur_clients.bind(('0.0.0.0', PORT_CLIENTS))
        serveur_clients.listen(5)
        print(f"Serveur maître (clients) en attente sur le port {PORT_CLIENTS}...")
        while True:
            try:
                conn_client, addr_client = serveur_clients.accept()
                print(f"Nouveau client connecté : {addr_client}")
                thread_client = threading.Thread(target=gerer_client, args=(conn_client, addr_client))
                thread_client.start()
            except KeyboardInterrupt:
                print("\nArrêt du serveur...")
                break

    except Exception as e:
        print(f"Erreur au démarrage du serveur : {e}")
    finally:
        serveur_clients.close()
        serveur_esclaves.close()
