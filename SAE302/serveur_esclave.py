import socket, argparse, os, threading, subprocess

etat_slave = True

def reception_code():
    global etat_slave
    print("Connexion établie avec le master.")
    while etat_slave:
        try:
            message = slave.recv(1024).decode()
            if not message:
                print("Master déconnecté ou message vide reçu.")
                break
            client_port, script = message.split(":", 1)
            threading.Thread(target=traiter_script, args=(script, client_port)).start()
        except (ConnectionResetError):
            print("Connexion perdue avec le master.")
            break
        except Exception as e:
            print(f"Erreur avec le master : {e}")
            break
    slave.close()
    print("Connexion fermée avec le master.")

def traiter_script(script, client_port):
    print(f"Traitement du script : {script} (Client Port: {client_port})")
    resultat = choix_language(script)
    result_with_port = f"{client_port}:{resultat}"
    slave.send(result_with_port.encode())
    print("Résultat renvoyé au master.")

def choix_language(script):
    if script.startswith("#python"):
        return execute_python(script)
    elif script.startswith("//c"):
        return execute_c(script)
    elif script.startswith("//java"):
        return execute_java(script)
    else:
        return "Erreur : Type de script non pris en charge."

def execute_python(script):
    try:
        process = subprocess.run(["python3", "-c", script], capture_output=True, text=True)
        return process.stdout if process.returncode == 0 else f"Erreur Python : {process.stderr}"
    except FileNotFoundError:
        return "Erreur : Compilateur Python non trouvé."
    except Exception as e:
        return f"Erreur : {e}"

def execute_c(script):
    try:
        with open("temp.c", "w") as f:
            f.write(script)
        compile_result = subprocess.run(["gcc", "temp.c", "-o", "temp"], capture_output=True, text=True)
        if compile_result.returncode != 0:
            return f"Erreur de compilation C : {compile_result.stderr}"
        exec_result = subprocess.run(["./temp"], capture_output=True, text=True)
        return exec_result.stdout if exec_result.returncode == 0 else f"Erreur à l'exécution C : {exec_result.stderr}"
    except FileNotFoundError:
        return "Erreur : Compilateur GCC non trouvé."
    except Exception as e:
        return f"Erreur lors de l'exécution C : {e}"
    finally:
        for file in ["temp.c", "temp"]:
            try:
                os.remove(file)
            except FileNotFoundError:
                pass

def execute_java(script):
    try:
        with open("Temp.java", "w") as f:
            f.write(script)
        compile_result = subprocess.run(["javac", "Temp.java"], capture_output=True, text=True)
        if compile_result.returncode != 0:
            return f"Erreur de compilation Java : {compile_result.stderr}"
        exec_result = subprocess.run(["java", "Temp"], capture_output=True, text=True)
        return exec_result.stdout if exec_result.returncode == 0 else f"Erreur à l'exécution Java : {exec_result.stderr}"
    except FileNotFoundError:
        return "Erreur : Compilateur Java (javac) non trouvé."
    except Exception as e:
        return f"Erreur lors de l'exécution Java : {e}"
    finally:
        for file in ["Temp.java", "Temp.class"]:
            try:
                os.remove(file)
            except FileNotFoundError:
                pass

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Serveur esclave qui exécute le code envoyé par le serveur maître.")
    parser.add_argument("--ip_m", type=str, default='127.0.0.1', help="Adresse IP du serveur maître.")
    parser.add_argument("--pm", type=int, default=4300, help="Port utilisé pour la connexion au master.")
    args = parser.parse_args()

    slave = socket.socket()
    try:
        slave.connect((args.ip_m, args.pm))
        print("Connecté au master.")
        reception_code()
    except (KeyboardInterrupt, OSError) as e:
        print(f"Arrêt ou erreur : {e}")
    finally:
        slave.close()
