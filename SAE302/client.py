
import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QGridLayout, QLabel, QLineEdit, QPushButton, QComboBox, QMessageBox, QTextEdit
from PyQt6.QtCore import QCoreApplication
import socket
import threading
client_connected = False

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        widget = QWidget()
        self.setCentralWidget(widget)

        grid = QGridLayout()
        widget.setLayout(grid)

        label_serveur = QLabel("Serveur :")
        label_port = QLabel("Port :")
        self.label_connected = QLabel('')
        self.label_connected.setObjectName('label_connected')
        self.bouton_connexion = QPushButton("Se connecter au serveur")
        self.input_serveur = QLineEdit()
        self.input_serveur.setText('127.0.0.1')
        self.input_port = QLineEdit()
        self.input_port.setText('4200')
        self.input_message = QTextEdit('')
        self.affichage = QTextEdit('')
        self.affichage.setEnabled(False)
        self.bouton_envoi = QPushButton('Envoyer le message')
        self.quit = QPushButton("Quitter")
        

        grid.addWidget(label_serveur, 0, 0, 1, 1)
        grid.addWidget(label_port, 0, 2, 1, 1)
        grid.addWidget(self.input_serveur, 0, 1, 1, 1)
        grid.addWidget(self.input_port, 0, 3, 1, 1)
        grid.addWidget(self.bouton_connexion, 1, 0, 1, 4)
        grid.addWidget(self.label_connected, 2, 0, 1, 4)
        grid.addWidget(self.quit, 5, 0, 1, 4)
        grid.addWidget(self.input_message, 3, 0, 1, 2)
        grid.addWidget(self.affichage, 3, 2, 2, 2)
        grid.addWidget(self.bouton_envoi, 4, 0, 1, 2)

        self.quit.clicked.connect(self.__quitter)
        self.bouton_connexion.clicked.connect(self.__connect)
        self.bouton_envoi.clicked.connect(self.__envoyer_message)



        self.setWindowTitle("Client Graphique")
        self.resize(500,500)


    def __quitter(self):
        QCoreApplication.exit(0)

    def __connect(self):
        global client_connected, client, addresse_serveur, port
        if client_connected :
            client.close()
            client_connected = False
            self.bouton_connexion.setText("Se connecter au serveur")
            self.label_connected.setText('Déconnecté du serveur')
            self.setStyleSheet('QLabel#label_connected{color: red;}')
        else:
            try:
                addresse_serveur = self.input_serveur.text()
                port = int(self.input_port.text())
            except ValueError:
                self.label_connected.setText("Veuillez entrer une valeur pour l'addresse et le port")
                self.setStyleSheet('QLabel#label_connected{color: red;}')
            else:
                client = socket.socket()    
                try :
                    client.connect((addresse_serveur, port))
                except ConnectionRefusedError or OSError:
                    self.label_connected.setText('Connection refusée')
                    self.setStyleSheet('QLabel#label_connected{color: red;}')
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
            except ConnectionResetError:
                print("Connexion perdue avec le serveur")
                break
            except ConnectionAbortedError:
                pass
            except OSError:
                exit()
            else:
                self.affichage.append(f'{message}\n')

    def __envoyer_message(self):
        if client_connected :
            message = self.input_message.toPlainText()
            client.send(message.encode())
        else :
            self.label_connected.setText("Impossible d'envoyer un message sans être connecté au serveur")
            self.setStyleSheet('QLabel#label_connected{color: red;}')


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())



