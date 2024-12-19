import socket, threading, os, subprocess

etat_slave = True

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
            thread = threading.Thread(target=traiter_script, args=(script,))
            thread.start()
        except ConnectionResetError:
            print(f"Connexion perdue avec le master.")
            etat_slave = False
        except Exception as e:
            print(f"Erreur avec le master : {e}")
            etat_slave = False
    slave.close()
    print(f"Connexion fermée avec le master.")

def traiter_script(script):
    resultat = choix_language(script)
    slave.send(resultat.encode())
    print(f"resultat renvoye au master")

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
    slave = socket.socket()
    print("En attente de connexion...")
    addresse_master = "127.0.0.1"
    port_master = 4301
    while etat_slave:
        try:
            slave.connect((addresse_master, port_master))
            print(f"connecte au master")
            reception_code()
        except KeyboardInterrupt:
            print("\nArrêt du serveur...")
            etat_slave = False
    slave.close()