from PyQt6.QtWidgets import QMainWindow
from PyQt6 import uic
from PyQt6.QtCore import Qt
from user import User

class MainWindow(QMainWindow):

    def __init__(self, user: User):
        super(MainWindow, self).__init__()
        uic.loadUi("ui/mainwindow.ui", self)

        self.__user = user

        print(f"Welcome {self.__user.get_username()}")

       
        self.setFixedSize(self.size())

    def on_pushButton_clicked(self):
        self.ui.label.setText("Hello World")
