# Architecture du projet

Le projet SAE302 est organisé de la manière suivante :

SAE302
│
├───README.txt              # Ce fichier
├───docs                     # Documentation générée avec Sphinx
│   ├───_build               # Dossier de build de la documentation
│   │   └───html             # Documentation HTML générée
│   ├───_static              # Fichiers statiques pour la documentation
│   ├───_templates           # Templates pour la documentation Sphinx
│   └───conf.py              # Configuration Sphinx
└───src                       # Dossier des fichiers sources du projet
    ├───client.py            # Code source du client graphique
    ├───serveur_esclave.py   # Code source du serveur esclave
    └───serveur_maitre.py    # Code source du serveur maître

# Description des dossiers

- /docs : Ce dossier contient toute la documentation du projet, générée via Sphinx. La documentation HTML est accessible dans le dossier `/docs/_build/html`. 
- /src : Ce dossier contient le code source du projet. Il est divisé en trois parties principales :
    - client.py : Le client graphique qui permet de se connecter à un serveur via un socket et d'envoyer des fichiers de code source pour exécution.
    - serveur_esclave.py : Le serveur esclave qui reçoit et exécute le code envoyé par le serveur maître.
    - serveur_maitre.py : Le serveur maître qui gère la connexion avec les clients et la distribution des tâches entre les serveurs esclaves et recueille les résultats.