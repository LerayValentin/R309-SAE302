import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QGridLayout, QLabel, QLineEdit, QPushButton, QTextEdit, QFileDialog
from PyQt6.QtCore import QCoreApplication
import socket
import threading

client_connected = False

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.file_path = ""

    def init_ui(self):
        widget = QWidget()
        self.setCentralWidget(widget)
        grid = QGridLayout()
        widget.setLayout(grid)

        label_serveur = QLabel("Serveur :")
        label_port = QLabel("Port :")
        self.label_connected = QLabel('')
        self.label_connected.setObjectName('label_connected')
        self.label_connected.setMaximumHeight(20)
        self.bouton_connexion = QPushButton("Se connecter au serveur")
        self.input_serveur = QLineEdit('127.0.0.1')
        self.input_port = QLineEdit('4200')
        self.text_editor = QTextEdit('')
        self.bouton_ouvrir = QPushButton('Ouvrir fichier')
        self.bouton_envoyer_fichier = QPushButton('Envoyer fichier')
        self.affichage = QTextEdit('')
        self.affichage.setEnabled(False)
        self.quit = QPushButton("Quitter")

        grid.addWidget(label_serveur, 0, 0)
        grid.addWidget(self.input_serveur, 0, 1)
        grid.addWidget(label_port, 0, 2)
        grid.addWidget(self.input_port, 0, 3)
        grid.addWidget(self.bouton_connexion, 1, 0, 1, 4)
        grid.addWidget(self.label_connected, 2, 0, 1, 4)
        grid.addWidget(self.bouton_ouvrir, 3, 0, 1, 2)
        grid.addWidget(self.bouton_envoyer_fichier, 3, 2, 1, 2)
        grid.addWidget(self.text_editor, 5, 0, 2, 2)
        grid.addWidget(self.affichage, 5, 2, 2, 2)
        #grid.addWidget(self.quit, 7, 0, 1, 4)

        #self.quit.clicked.connect(self.__quitter)
        self.bouton_connexion.clicked.connect(self.__connect)
        self.bouton_ouvrir.clicked.connect(self.__ouvrir_fichier)
        self.bouton_envoyer_fichier.clicked.connect(self.__envoyer_fichier)

        self.setWindowTitle("Client Graphique")
        self.resize(800, 800)


    def __connect(self):
        global client_connected, client, addresse_serveur, port
        if client_connected:
            client.close()
            client_connected = False
            self.bouton_connexion.setText("Se connecter au serveur")
            self.label_connected.setText('Déconnecté du serveur')
            self.setStyleSheet('QLabel#label_connected{color: red;}')
        else:
            try:
                addresse_serveur = self.input_serveur.text()
                port = int(self.input_port.text())
                client = socket.socket()
                client.connect((addresse_serveur, port))
            except Exception as e:
                self.label_connected.setText(f"Erreur : {e}")
            else:
                client_connected = True
                self.label_connected.setText('Connecté au serveur')
                self.setStyleSheet('QLabel#label_connected{color: green;}')
                self.bouton_connexion.setText("Se déconnecter du serveur")
                thread_reception = threading.Thread(target=self.__recevoir_messages)
                thread_reception.start()

    def __recevoir_messages(self):
        while client_connected:
            try:
                message = client.recv(1024).decode()
                self.affichage.append(message)
            except Exception:
                break

    def __ouvrir_fichier(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Ouvrir un fichier", "", "Source Files (*.py *.c *.java);;All Files (*)")
        if file_path:
            with open(file_path, 'r') as file:
                contenu = file.read()
            if file_path.endswith('.c'):
                commentaire = "//c\n"
            elif file_path.endswith('.java'):
                commentaire = "//java\n"
            elif file_path.endswith('.py'):
                commentaire = "#python\n"

            contenu_modifie = commentaire + contenu
            self.text_editor.setText(contenu_modifie)

    def __envoyer_fichier(self):
        if client_connected:
            contenu = self.text_editor.toPlainText()
            client.send(contenu.encode())
        else:
            self.label_connected.setText("Connectez-vous d'abord au serveur.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
    
"""
    def __quitter(self):
        client.close()
        QCoreApplication.exit(0)
"""