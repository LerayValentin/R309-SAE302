import socket, threading, argparse

esclaves_actifs = []
charge_esclaves = {}
clients_connectes = {}
scripts_en_attente = {}
lock = threading.Lock()

def gerer_client(conn, addr):
    print(f"Client connecté : {addr}")
    while True:
        try:
            script = conn.recv(1024).decode()
            if not script:
                break
            with lock:
                scripts_en_attente[addr[1]] = script
            result = redistribuer_script(script, addr[1])
            if result != "Script envoyé à l'esclave.":
                conn.send(result.encode())
        except Exception as e:
            print(f"Erreur avec le client {addr}: {e}")
            break
    conn.close()
    with lock:
        clients_connectes.pop(addr[1], None)

def redistribuer_script(script, client_port, esclaves_exclus=None):
    if esclaves_exclus is None:
        esclaves_exclus = set()
    with lock:
        esclaves_disponibles = [
            (conn, addr)
            for conn, addr in esclaves_actifs
            if charge_esclaves.get(addr, 0) < nbr_prog_max and addr not in esclaves_exclus
        ]
        print(f"Esclaves disponibles : {esclaves_disponibles}")
        if not esclaves_disponibles:
            return "Erreur : Aucun esclave disponible pour executer le script."

        for esclave_conn, esclave_addr in esclaves_disponibles:
            try:
                message = f"{client_port}:{script}"
                print(f"Envoi du script au esclave {esclave_addr} : {message}")
                esclave_conn.sendall(message.encode())
                charge_esclaves[esclave_addr] = charge_esclaves.get(esclave_addr, 0) + 1
                return "Script envoyé à l'esclave."
            except Exception as e:
                print(f"Erreur avec l'esclave {esclave_addr}: {e}")
                esclaves_actifs.remove((esclave_conn, esclave_addr))
                charge_esclaves.pop(esclave_addr, None)
                esclave_conn.close()
                esclaves_exclus.add(esclave_addr)

        return redistribuer_script(script, client_port, esclaves_exclus)

def ecouter_esclave(esclave_conn, esclave_addr):
    while True:
        try:
            reponse = esclave_conn.recv(1024).decode()
            if not reponse:
                break
            if "Erreur: Compilateur manquant" in reponse:
                client_port, _ = reponse.split(":", 1)
                print(f"Compilateur manquant sur l'esclave {esclave_addr}. Redistribution du script.")
                with lock:
                    script = scripts_en_attente.get(int(client_port), "Script introuvable")
                    redistribuer_script(script, int(client_port), esclaves_exclus={esclave_addr})
                continue
            client_port, resultat = reponse.split(":", 1)
            with lock:
                client_conn = clients_connectes.get(int(client_port))
                if client_conn:
                    client_conn.send(resultat.encode())
                if charge_esclaves.get(esclave_addr, 0) > 0:
                    charge_esclaves[esclave_addr] -= 1
        except Exception as e:
            print(f"Erreur de réception avec l'esclave {esclave_addr}: {e}")
            break
    with lock:
        esclaves_actifs.remove((esclave_conn, esclave_addr))
        charge_esclaves.pop(esclave_addr, None)
    esclave_conn.close()
    print(f"Esclave {esclave_addr} déconnecté.")

def accepter_slave():
    while True:
        try:
            slave_conn, slave_addr = serveur_esclaves.accept()
            with lock:
                esclaves_actifs.append((slave_conn, slave_addr))
                charge_esclaves[slave_addr] = 0
            print(f"Esclave connecté depuis {slave_addr}. Total : {len(esclaves_actifs)}")
            threading.Thread(target=ecouter_esclave, args=(slave_conn, slave_addr)).start()
        except Exception as e:
            print(f"Erreur lors de l'acceptation d'un esclave : {e}")
            break

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Serveur maître pour clients et esclaves.")
    parser.add_argument("--pc", type=int, default=4200, help="Port pour les connexions clients (par defaut : 4200).")
    parser.add_argument("--pe", type=int, default=4300, help="Port pour les connexions esclaves (par défaut : 4300).")
    parser.add_argument("--nbr_p", type=int, default=2, help="Nombre maximum de programmes simultanes par serveur esclave")
    args = parser.parse_args()

    serveur_clients = socket.socket()
    serveur_esclaves = socket.socket()
    nbr_prog_max = args.nbr_p

    try:
        serveur_esclaves.bind(('0.0.0.0', args.pe))
        serveur_esclaves.listen()
        print(f"Serveur maître (esclaves) sur le port {args.pe}...")
        threading.Thread(target=accepter_slave, daemon=True).start()

        serveur_clients.bind(('0.0.0.0', args.pc))
        serveur_clients.listen()
        print(f"Serveur maître (clients) sur le port {args.pc}...")

        while True:
            try:
                conn_client, addr_client = serveur_clients.accept()
                with lock:
                    clients_connectes[addr_client[1]] = conn_client
                threading.Thread(target=gerer_client, args=(conn_client, addr_client)).start()
            except KeyboardInterrupt:
                print("\nArrêt du serveur...")
                break
    except Exception as e:
        print(f"Erreur au démarrage du serveur : {e}")
    finally:
        serveur_clients.close()
        serveur_esclaves.close()
