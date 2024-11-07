try:
    fichier = open("fichier.txt", "r")
except FileNotFoundError: #si erreur Fichier non trouvé
    print("Fichier non trouve")
else:
    print(fichier.read())
finally:
    try:
        fichier.close()
    except NameError:
        print("Le fichier n'a pas ete ouvert")