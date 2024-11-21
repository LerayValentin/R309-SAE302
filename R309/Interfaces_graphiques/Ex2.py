import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QGridLayout, QLabel, QLineEdit, QPushButton, QComboBox, QMessageBox
from PyQt6.QtCore import Qt


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        widget = QWidget()
        self.setCentralWidget(widget)

        grid = QGridLayout()
        widget.setLayout(grid)

        label_temp = QLabel("Température :")
        self.input_temp = QLineEdit()
        self.input_temp.setPlaceholderText("Entrez une valeur numérique")
        self.label_unite1 = QLabel("°C")
        self.bouton_conversion = QPushButton("Convertir")
        self.label_conversion = QLabel("Conversion :")
        self.resultat = QLineEdit()
        self.resultat.setEnabled(False)
        self.label_unite2 = QLabel("K")
        self.choix_unite = QComboBox()
        self.choix_unite.addItems(["°C -> K", "K -> °C"])
        self.bouton_aide = QPushButton("?")
        self.bouton_aide.setFixedSize(30, 30)

        grid.addWidget(label_temp, 0, 0)
        grid.addWidget(self.input_temp, 0, 1)
        grid.addWidget(self.label_unite1, 0, 2)
        grid.addWidget(self.bouton_conversion, 1, 1)
        grid.addWidget(self.label_conversion, 2, 0)
        grid.addWidget(self.resultat, 2, 1)
        grid.addWidget(self.label_unite2, 2, 2)
        grid.addWidget(self.choix_unite, 1, 3, 1, 2)
        grid.addWidget(self.bouton_aide, 3, 4)

        self.bouton_conversion.clicked.connect(self.conversion_temp)
        self.choix_unite.currentIndexChanged.connect(self.changement_unite)
        self.bouton_aide.clicked.connect(self.aide)

        self.setWindowTitle("Conversion de Température")
        self.resize(375,200)
        self.setStyleSheet('''
            QMainWindow{
                background: rgb(32,34,168);
                }
            QPushButton{
                font-family: "Comic Sans MS";
                background-color: yellow; 
                color:black;
                
                }             
            ''')



    def conversion_temp(self):
        try:
            temp = float(self.input_temp.text())
            if self.choix_unite.currentText() == "°C -> K":
                if temp < -273.15:
                    self.afficher_erreur("La température ne peut pas être inférieure à -273,15 °C.")
                    return
                else:
                    temp_convertie = temp + 273.15
                    self.resultat.setText(f"{temp_convertie}")
            else:
                if temp < 0:
                    self.afficher_erreur("La température ne peut pas être inférieure à 0 K.")
                    return
                else:
                    temp_convertie = temp - 273.15
                    self.resultat.setText(f"{temp_convertie}")

        except ValueError:
            self.afficher_erreur("Veuillez entrer une valeur numérique valide.")


    def changement_unite(self):
        if self.choix_unite.currentText() == "°C -> K":
            self.label_unite1.setText("°C")
            self.label_unite2.setText("K")
        else:
            self.label_unite1.setText("K")
            self.label_unite2.setText("°C")

    def aide(self):
        QMessageBox.information( self, "Aide", "Permet de convertir un nombre soit de Kelvin vers Celcius, soit de Celcius vers Kelvin")

    def afficher_erreur(self, message):
        QMessageBox.critical(self, "Erreur", message)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
