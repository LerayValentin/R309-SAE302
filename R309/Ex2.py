
try:
    fichier = open("fichier.txt", "r")
except FileNotFoundError: #Fichier non trouvé
    print("Fichier non trouvé")
else:
    print(fichier.read())
    fichier.close()