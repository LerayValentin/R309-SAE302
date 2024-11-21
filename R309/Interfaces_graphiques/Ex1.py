import sys
from PyQt6.QtWidgets import QApplication, QLabel, QLineEdit, QPushButton, QWidget, QMainWindow, QGridLayout
from PyQt6.QtCore import QCoreApplication

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        widget = QWidget()
        self.setCentralWidget(widget)

        grid = QGridLayout()
        widget.setLayout(grid)

        lab = QLabel("Saisir votre nom")
        self.text = QLineEdit("")
        ok = QPushButton("Ok")
        quit = QPushButton("Quitter")
        self.bjr = QLabel("")

        grid.addWidget(lab, 0, 0, 1, 2)
        grid.addWidget(self.text, 1, 0, 1, 2)
        grid.addWidget(ok, 2, 0, 1, 2)
        grid.addWidget(self.bjr, 3, 0, 1, 2) 
        grid.addWidget(quit, 4, 0, 1, 2) 

        ok.clicked.connect(self.__actionOk)
        quit.clicked.connect(self.__actionQuitter)

        self.setWindowTitle("Une première fenêtre")
        self.resize(300,150)

    def __actionOk(self):
        name = self.text.text().strip()
        if name:
            self.bjr.setText(f"Bonjour {name}")
        else:
            self.bjr.setText("Veuillez entrer un nom.")

    def __actionQuitter(self):
        QCoreApplication.exit(0)


if __name__ == '__main__':
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    app.exec()
