import os
print("Repertoire courant :", os.getcwd())

nom_fichier = "../R309-SAE302/R309/Exceptions/fichier.txt"

try:
    with open(nom_fichier, 'r') as fichier:
        for ligne in fichier:
            ligne = ligne.rstrip("\n\r")
            print(ligne, end=' ')

except FileNotFoundError:
    print("Fichier introuvable.")
except IOError:
    print("Erreur d'entrée/sortie")
except FileExistsError:
    print("Le fichier existe déjà")
except PermissionError:
    print("Pas les permissions nécessaires")
finally:
    print("Programme execute.")
