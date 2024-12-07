from PyQt6.QtWidgets import QDialog
from PyQt6 import uic

class LoginForm(QDialog):

    def __init__(self):
        super(LoginForm, self).__init__()
        uic.loadUi("ui/loginform.ui", self)

    def on_pushButton_clicked(self):
        self.ui.label.setText("Hello World")