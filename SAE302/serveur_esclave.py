import socket
import threading
import os
import subprocess
import argparse
from queue import Queue

etat_slave = True
queue = Queue()

def reception_code():
    global etat_slave
    print(f"Connexion établie avec le master.")
    while etat_slave:
        try:
            script = slave.recv(1024).decode()
            if not script:
                print(f"Master déconnecté.")
                etat_slave = False
                break
            queue.put(script)
        except ConnectionResetError:
            print(f"Connexion perdue avec le master.")
            etat_slave = False
        except Exception as e:
            print(f"Erreur avec le master : {e}")
            etat_slave = False
    slave.close()
    print(f"Connexion fermée avec le master.")

def traiter_script():
    while etat_slave:
        if not queue.empty():
            script = queue.get()
            print(f"Traitement du script : {script}")
            resultat = choix_language(script)
            print(resultat)
            slave.send(resultat.encode())
            print(f"Resultat renvoyé au master")
            queue.task_done()

def choix_language(script):
    if script.startswith("#python"):
        return execute_python(script)
    elif script.startswith("//c"):
        return execute_c(script)
    elif script.startswith("//java"):
        return execute_java(script)
    else:
        return "Type de script non pris en charge."

def execute_python(script):
    try:
        process = subprocess.Popen(["python3", "-c", script], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        stdout, stderr = process.communicate()
    except Exception as e:
        return f"Erreur : {e}"
    else:
        if process.returncode != 0:
            return f"Erreur Python : {stderr}"
        else:
            return stdout

def execute_c(script):
    try:
        with open("temp.c", "w") as f:
            f.write(script)
        compile_result = subprocess.run(["gcc", "temp.c", "-o", "temp"], stderr=subprocess.PIPE, text=True)
        if compile_result.returncode != 0:
            return f"Erreur de compilation C : {compile_result.stderr}"
        exec_result = subprocess.run(["./temp"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        os.remove("temp.c")
        os.remove("temp")
    except Exception as e:
        return f"Erreur lors de l'exécution C : {e}"
    else:
        if exec_result.returncode != 0:
            return f"Erreur à l'exécution C : {exec_result.stderr}"
        else:
            return exec_result.stdout

def execute_java(script):
    try:
        with open("Temp.java", "w") as f:
            f.write(script)
        compile_result = subprocess.run(["javac", "Temp.java"], stderr=subprocess.PIPE, text=True)
        if compile_result.returncode != 0:
            return f"Erreur de compilation Java : {compile_result.stderr}"
        exec_result = subprocess.run(["java", "Temp"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        os.remove("Temp.java")
        os.remove("Temp.class")
    except Exception as e:
        return f"Erreur lors de l'exécution Java : {e}"
    else:
        if exec_result.returncode != 0:
            return f"Erreur à l'exécution Java : {exec_result.stderr}"
        else:
            return exec_result.stdout

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Serveur esclave qui exécute le code envoyé par le serveur maître")
    parser.add_argument("--ip_m", type=str, default='127.0.0.1', help="Adresse IP du serveur maître (au format X.X.X.X).")
    parser.add_argument("--pm", type=int, default=4300, help="Port utilisé pour la connexion au master (par défaut : 4300).")
    args = parser.parse_args()

    addresse_master = args.ip_m
    port_master = args.pm

    slave = socket.socket()
    print("En attente de connexion...")
    while etat_slave:
        try:
            slave.connect((addresse_master, port_master))
            print(f"Connecté au master.")
            thread_reception = threading.Thread(target=reception_code)
            thread_reception.start()
            thread_traitement = threading.Thread(target=traiter_script)
            thread_traitement.start()
            thread_reception.join()
            thread_traitement.join()
        except KeyboardInterrupt:
            print("\nArrêt du serveur...")
            etat_slave = False
        except OSError as e:
            print(f"Erreur de connexion au master : {e}")
            etat_slave = False
        finally:
            if slave:
                slave.close()
