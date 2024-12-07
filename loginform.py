from PyQt6.QtWidgets import QDialog
from PyQt6 import uic
import sys

class LoginForm(QDialog):

    def __init__(self):
        super(LoginForm, self).__init__()
        uic.loadUi("ui/loginform.ui", self)

        self.loginbtn.clicked.connect(self.login)
        self.newuserbtn.clicked.connect(self.newuser)

        self.__username: str = ""
        self.__password: str = ""
    
    def login(self):
        self.__username = self.username.text()
        self.__password = self.password.text()
        self.hide()
    
    def newuser(self):
        self.close()
    
    def get_username(self):
        return self.__username
    
    def get_password(self):
        return self.__password
    
    def closeEvent(self, event):
        sys.exit(0)