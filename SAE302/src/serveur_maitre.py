"""
Serveur maître pour gérer les connexions des clients et redistribuer les scripts reçus aux serveurs esclaves.

Ce serveur gère les connexions des clients pour recevoir des scripts Python, Java, et C,
et les redistribue aux esclaves actifs selon les langages qu'ils sont capables de gérer et leur charge actuelle.
"""

import socket, threading, argparse

# Variable globale pour indiquer l'état de l'esclave
etat_master = True

# Dictionnaires globaux pour gérer les esclaves, les charges langages qu'ils sont capables de gérer, et les clients connectés
esclaves_actifs = {}
charge_esclaves = {}
clients_connectes = {}
lock = threading.Lock()


def gerer_client(conn: socket.socket, addr: tuple):
    """
    Gère un client connecté.

    Args:
        conn (socket.socket): La connexion socket avec le client.
        addr (tuple): L'adresse (IP, port) du client.
    """
    print(f"Client connecté : {addr}")
    while True:
        try:
            script = conn.recv(16384).decode()
            if not script:
                break
            result = redistribuer_script(script, addr[1])
            conn.send(result.encode())
        except Exception as e:
            print(f"Erreur avec le client {addr}: {e}")
            break
    conn.close()
    with lock:
        clients_connectes.pop(addr[1], None)


def redistribuer_script(script: str, client_port: int) -> str:
    """
    Redistribue un script reçu d'un client à un esclave actif approprié.

    Args:
        script (str): Le script reçu du client.
        client_port (int): Le port du client.

    Returns:
        str: Un message indiquant le résultat de la redistribution.
    """
    with lock:
        if script.startswith("//c"):
            compilateur = "gcc"
        elif script.startswith("//java"):
            compilateur = "javac"
        elif script.startswith("#python"):
            compilateur = None
        else:
            return "Erreur : Type de script non pris en charge."

        if compilateur is None:
            esclaves_disponibles = [
                (addr, esclaves_actifs[addr]) for addr in esclaves_actifs
                if charge_esclaves.get(addr, 0) < nbr_prog_max
            ]
        else:
            esclaves_disponibles = [
                (addr, esclaves_actifs[addr]) for addr in esclaves_actifs
                if esclaves_actifs[addr].get(compilateur, False) and charge_esclaves.get(addr, 0) < nbr_prog_max
            ]

        if not esclaves_disponibles:
            if esclaves_actifs:
                return f"Erreur : Aucun esclave disponible pour le compilateur {compilateur or 'python'}."
            return "Erreur : Aucun esclave connecté au maître."

        esclave_addr, esclave_info = esclaves_disponibles[0]
        esclave_conn = esclave_info["conn"]

        try:
            message = f"{client_port}§§§{script}"
            esclave_conn.sendall(message.encode())
            charge_esclaves[esclave_addr] += 1
            return "Script envoyé à l'esclave."
        except Exception as e:
            print(f"Erreur avec l'esclave {esclave_addr}: {e}")
            esclaves_actifs.pop(esclave_addr, None)
            charge_esclaves.pop(esclave_addr, None)
            return redistribuer_script(script, client_port)


def ecouter_esclave(esclave_conn: socket.socket, esclave_addr: tuple):
    """
    Écoute les réponses des esclaves et les retransmet aux clients.

    Args:
        esclave_conn (socket.socket): La connexion socket avec l'esclave.
        esclave_addr (tuple): L'adresse (IP, port) de l'esclave.
    """
    while True:
        try:
            reponse = esclave_conn.recv(16384).decode()
            if not reponse:
                break
            client_port, resultat = reponse.split("§§§", 1)
            with lock:
                client_conn = clients_connectes.get(int(client_port))
                if client_conn:
                    client_conn.send(resultat.encode())
                if charge_esclaves.get(esclave_addr, 0) > 0:
                    charge_esclaves[esclave_addr] -= 1
        except Exception as e:
            print(f"Erreur avec l'esclave {esclave_addr}: {e}")
            break
    with lock:
        esclaves_actifs.pop(esclave_addr, None)
        charge_esclaves.pop(esclave_addr, None)
    esclave_conn.close()
    print(f"Esclave {esclave_addr} déconnecté.")


def accepter_slave():
    """
    Accepte les connexions des esclaves et les ajoute à la liste des esclaves actifs 
    ainsi que les langages qu'ils sont capables de traiter.
    """
    while True:
        try:
            slave_conn, slave_addr = serveur_esclaves.accept()
            compilateurs = slave_conn.recv(1024).decode()
            gcc_present = "gcc:1" in compilateurs
            javac_present = "javac:1" in compilateurs
            with lock:
                esclaves_actifs[slave_addr] = {"conn": slave_conn, "gcc": gcc_present, "javac": javac_present}
                charge_esclaves[slave_addr] = 0
            print(f"Esclave {slave_addr} connecté avec capacités : gcc={gcc_present}, javac={javac_present}")
            threading.Thread(target=ecouter_esclave, args=(slave_conn, slave_addr)).start()
        except Exception as e:
            print(f"Erreur lors de l'acceptation d'un esclave : {e}")
            break


def main():
    """
    Point d'entrée principal du programme.

    Configure et démarre les serveurs pour les clients et les esclaves.
    """
    parser = argparse.ArgumentParser(description="Serveur maître pour clients et esclaves.")
    parser.add_argument("--pc", type=int, default=4200, help="Port pour les connexions clients (par defaut : 4200).")
    parser.add_argument("--pe", type=int, default=4300, help="Port pour les connexions esclaves (par defaut : 4300).")
    parser.add_argument("--nbr_p", type=int, default=2, help="Nombre maximum de programmes simultanés par esclave (par defaut : 2).")
    args = parser.parse_args()

    global nbr_prog_max
    nbr_prog_max = args.nbr_p

    global serveur_clients, serveur_esclaves
    serveur_clients = socket.socket()
    serveur_esclaves = socket.socket()

    try:
        serveur_esclaves.bind(('0.0.0.0', args.pe))
        serveur_esclaves.listen()
        print(f"Serveur maître (esclaves) sur le port {args.pe}...")
        threading.Thread(target=accepter_slave, daemon=True).start()

        serveur_clients.bind(('0.0.0.0', args.pc))
        serveur_clients.listen()
        print(f"Serveur maître (clients) sur le port {args.pc}...")

        while True:
            conn_client, addr_client = serveur_clients.accept()
            with lock:
                clients_connectes[addr_client[1]] = conn_client
            threading.Thread(target=gerer_client, args=(conn_client, addr_client)).start()
    except Exception as e:
        print(f"Erreur au démarrage du serveur : {e}")
    finally:
        serveur_clients.close()
        serveur_esclaves.close()


if __name__ == "__main__":
    main()