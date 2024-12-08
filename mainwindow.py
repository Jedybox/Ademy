from PyQt6.QtWidgets import QMainWindow
from PyQt6 import uic
from PyQt6.QtCore import Qt
from User import User
from Dialogs import Login, Register

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        uic.loadUi('ui/mainwindow.ui', self)

        self.setFixedSize(self.size())


        self.__user: User = User()

        while True:
            login: Login = Login()
            login.exec()

            print(login.result())

            if login.result() == 1:
                self.__user.set_username(login.username.text())
                self.__user.set_password(login.password.text())
                break
            else:
                register = Register()
                register.exec()
                
        
        self.show()
        

        