import socket, threading, os, sys, io


etat_serveur = True

def gerer_client(conn, addr):
    global etat_serveur
    global client_connected
    print(f"Connexion établie avec {addr}")
    
    while client_connected:
        try:
            script = conn.recv(10240).decode()
            if not script:
                break
            print(f"Script reçu de {addr} :\n{script}")
            if script.startswith("//java"):
                result = execute_java(script)
            elif script.startswith("//c"):
                result = execute_c(script)
            elif script.startswith("#python"):
                result = execute_python(script)
            conn.send(result.encode())
        
        except ConnectionResetError:
            print(f"Connexion perdue avec {addr}")
            break
    conn.close()
    print(f"Connexion fermée avec {addr}")

def execute_python(script):
    try:
        output = io.StringIO()
        sys.stdout = output
        exec(script)
        return output.getvalue() or "Exécution réussie sans sortie."
    except Exception as e:
        sys.stdout = sys.__stdout__
        return f"Erreur lors de l'exécution Python : {str(e)}"

def execute_c(script):
    try:
        with open("temp.c", "w") as f:
            f.write(script)
        compile_result = os.system("gcc temp.c -o temp")
        if compile_result != 0:
            return "Erreur : Échec de la compilation C."

        result = os.popen("./temp").read()
        os.remove("temp.c")
        os.remove("temp")
    except Exception as e:
        return f"Erreur lors de l'exécution C : {str(e)}"
    else:
        return result or "Exécution réussie sans sortie."

def execute_java(script):
    try:
        with open("Temp.java", "w") as f:
            f.write(script)

        compile_result = os.system("javac Temp.java")
        if compile_result != 0:
            return "Erreur : Échec de la compilation Java."

        result = os.popen("java Temp").read()
        os.remove("Temp.java")
        os.remove("Temp.class")
    except Exception as e:
        return f"Erreur lors de l'exécution Java : {str(e)}"
    else:
        return result or "Exécution réussie sans sortie."

serveur = socket.socket()
serveur.bind(('0.0.0.0', 4200))
serveur.listen(5)

print("En attente de connexion...")

while etat_serveur:
    try:
        conn, addr = serveur.accept()
        client_connected = True
    except OSError:
        pass
    else:
        thread = threading.Thread(target=gerer_client, args=(conn, addr))
        thread.start()
