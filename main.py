import sys
from PyQt6.QtWidgets import QApplication

from mainwindow import MainWindow
from dialogs import LoginForm

from user import User

if __name__ == "__main__":
    app = QApplication(sys.argv)

    login = LoginForm()
    login.exec()

    if login.get_username() and login.get_password():

        user: User = User(login.get_username(), login.get_password())

        mainwindow: MainWindow = MainWindow(user)
        mainwindow.show()
    
    sys.exit(app.exec())
