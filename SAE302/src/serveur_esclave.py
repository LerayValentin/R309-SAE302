"""
Serveur esclave qui exécute les scripts reçus du serveur maître.

Ce script gère l'exécution des scripts en Python, C, ou Java envoyés par le maître.
Il communique avec le maître pour indiquer ses compilateurs disponibles et retourne les résultats des exécutions.
"""

import socket, threading, subprocess, argparse, os, shutil, random

# Variable globale pour indiquer l'état de l'esclave
etat_slave = True


def reception_code():
    """
    Écoute les messages du maître et traite les scripts reçus.

    Les scripts reçus sont exécutés dans des threads distincts. Si la connexion est perdue,
    la fonction se termine.
    """
    global etat_slave
    print("Connexion établie avec le master.")
    while etat_slave:   
        try:
            message = slave.recv(16384).decode()
            if not message:
                print("Master déconnecté ou message vide reçu.")
                etat_slave = False
                break
            client_port, script = message.split("§§§")
            threading.Thread(target=traiter_script, args=(script, client_port)).start()
        except ConnectionResetError:
            print("Connexion perdue avec le master.")
            etat_slave = False
            break
        except Exception as e:
            print(f"Erreur avec le master : {e}")
            etat_slave = False
            break
    slave.close()
    print("Connexion fermée avec le master.")


def traiter_script(script: str, client_port: str):
    """
    Traite un script reçu du maître.

    Args:
        script (str): Le script à exécuter.
        client_port (str): Le port du client associé au script.

    Envoie les résultats au maître après exécution.
    """
    try:
        resultat = choix_language(script)
        result_with_port = f"{client_port}§§§{resultat}"
        slave.send(result_with_port.encode())
    except ValueError as ve:
        print(f"Erreur dans les données reçues : {ve}")
        slave.send(f"{client_port}:Erreur dans les données reçues".encode())
    except Exception as e:
        print(f"Erreur lors du traitement du script : {e}")
        slave.send(f"{client_port}:Erreur interne : {e}".encode())


def choix_language(script: str) -> str:
    """
    Détermine le langage du script et appelle la fonction d'exécution appropriée.

    Args:
        script (str): Le script à exécuter.

    Returns:
        str: Le résultat de l'exécution du script.
    """
    if script.startswith("#python"):
        return execute_python(script)
    elif script.startswith("//c"):
        return execute_c(script)
    elif script.startswith("//java"):
        return execute_java(script)
    else:
        return "Erreur : Type de script non pris en charge."


def execute_python(script: str) -> str:
    """
    Exécute un script Python.

    Args:
        script (str): Le script Python à exécuter.

    Returns:
        str: Le résultat ou l'erreur de l'exécution.
    """
    try:
        process = subprocess.run(["python3", "-c", script], capture_output=True, text=True)
        return process.stdout if process.returncode == 0 else f"Erreur Python : {process.stderr}"
    except Exception as e:
        return f"Erreur : {e}"


def execute_c(script: str) -> str:
    """
    Compile et exécute un script en C.

    Args:
        script (str): Le script C à exécuter.

    Returns:
        str: Le résultat ou l'erreur de l'exécution.
    """
    try:
        nom_temporaire = f"temp_{random.randint(0, 9999)}.c"
        nom_sans_extension = nom_temporaire.split(".")[0]
        with open(nom_temporaire, "w") as f:
            f.write(script)
        compile_result = subprocess.run(["gcc", nom_temporaire, "-o", nom_sans_extension], capture_output=True, text=True)
        if compile_result.returncode != 0:
            return f"Erreur de compilation C : {compile_result.stderr}"
        exec_result = subprocess.run([f"./{nom_sans_extension}"], capture_output=True, text=True)
        return exec_result.stdout if exec_result.returncode == 0 else f"Erreur à l'exécution C : {exec_result.stderr}"
    except Exception as e:
        return f"Erreur lors de l'exécution C : {e}"
    finally:
        for file in [nom_temporaire, nom_sans_extension]:
            try:
                os.remove(file)
            except FileNotFoundError:
                pass


def execute_java(script: str) -> str:
    """
    Compile et exécute un script en Java.

    Args:
        script (str): Le script Java à exécuter.

    Returns:
        str: Le résultat ou l'erreur de l'exécution.
    """
    try:
        nom_temporaire = f"Temp_{random.randint(0, 9999)}.java"
        nom_classe = nom_temporaire.split(".")[0]
        with open(nom_temporaire, "w") as f:
            f.write(script)

        # Changement du nom de la classe dans le fichier Java pour éviter des erreurs lors de l'execution de plusieurs codes simultanément
        with open(nom_temporaire, "r") as fichier:
            lignes = fichier.readlines()
        for i, ligne in enumerate(lignes):
            if ligne.strip().startswith("public class"):
                mots = ligne.split()
                if len(mots) > 2:
                    mots[2] = nom_classe
                    lignes[i] = " ".join(mots) + "\n"
                break
        with open(nom_temporaire, "w") as fichier:
            fichier.writelines(lignes)

        compile_result = subprocess.run(["javac", nom_temporaire], capture_output=True, text=True)
        if compile_result.returncode != 0:
            return f"Erreur de compilation Java : {compile_result.stderr}"
        exec_result = subprocess.run(["java", nom_classe], capture_output=True, text=True)
        return exec_result.stdout if exec_result.returncode == 0 else f"Erreur à l'exécution Java : {exec_result.stderr}"
    except Exception as e:
        return f"Erreur lors de l'exécution Java : {e}"
    finally:
        for file in [nom_temporaire, f"{nom_classe}.class"]:
            try:
                os.remove(file)
            except FileNotFoundError:
                pass


def verifier_compilateurs() -> str:
    """
    Vérifie la présence des compilateurs gcc et javac.

    Returns:
        str: Une chaîne indiquant la présence des compilateurs.
    """
    gcc_present = "gcc:1" if shutil.which("gcc") else "gcc:0"
    javac_present = "javac:1" if shutil.which("javac") else "javac:0"
    return f"{gcc_present};{javac_present}"


def main():
    """
    Point d'entrée principal du programme.

    Établit une connexion avec le serveur maître et commence à écouter les scripts.
    """
    global slave
    parser = argparse.ArgumentParser(description="Serveur esclave qui exécute le code envoyé par le serveur maître.")
    parser.add_argument("--ip_m", type=str, default='127.0.0.1', help="Adresse IP du serveur maître (par defaut : localhost).")
    parser.add_argument("--pm", type=int, default=4300, help="Port utilisé pour la connexion au master (par defaut : 4300).")
    args = parser.parse_args()

    slave = socket.socket()
    try:
        slave.connect((args.ip_m, args.pm))
        print("Connecté au master.")
        compilateurs = verifier_compilateurs()
        slave.send(compilateurs.encode())
        reception_code()
    except (KeyboardInterrupt, OSError) as e:
        print(f"Arrêt ou erreur : {e}")
    finally:
        slave.close()


if __name__ == "__main__":
    main()
