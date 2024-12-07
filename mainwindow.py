from PyQt6.QtWidgets import QMainWindow
from PyQt6 import uic, QtWidgets

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        uic.loadUi("ui/mainwindow.ui", self)

    def on_pushButton_clicked(self):
        self.ui.label.setText("Hello World")
