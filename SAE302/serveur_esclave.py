import socket, threading, os, subprocess

etat_serveur = True

def gerer_client(conn, addr):
    print(f"Connexion établie avec {addr}")
    while True:
        try:
            script = conn.recv(1024).decode()
            if not script:
                print(f"Client {addr} déconnecté.")
                break
            result = traiter_script(script)
            conn.send(result.encode())
        except ConnectionResetError:
            print(f"Connexion perdue avec {addr}.")
            break
        except Exception as e:
            print(f"Erreur avec le client {addr}: {e}")
            break
    conn.close()
    print(f"Connexion fermée avec {addr}")

def traiter_script(script):
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
        if process.returncode != 0:
            return f"Erreur Python : {stderr}"
        return stdout
    except Exception as e:
        return f"Erreur : {e}"

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
        if exec_result.returncode != 0:
            return f"Erreur à l'exécution C : {exec_result.stderr}"
        return exec_result.stdout
    except Exception as e:
        return f"Erreur lors de l'exécution C : {e}"

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
        if exec_result.returncode != 0:
            return f"Erreur à l'exécution Java : {exec_result.stderr}"
        return exec_result.stdout
    except Exception as e:
        return f"Erreur lors de l'exécution Java : {e}"

serveur = socket.socket()
serveur.bind(('0.0.0.0', 4200))
serveur.listen(5)
print("En attente de connexions...")

while etat_serveur:
    try:
        conn, addr = serveur.accept()
        print(f"Nouveau client connecté : {addr}")
        thread = threading.Thread(target=gerer_client, args=(conn, addr))
        thread.start()
    except KeyboardInterrupt:
        print("\nArrêt du serveur...")
        etat_serveur = False
        break

serveur.close()
