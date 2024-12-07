import sys
from PyQt6.QtWidgets import QApplication

from mainwindow import MainWindow
from loginform import LoginForm

if __name__ == "__main__":
    app = QApplication(sys.argv)

    login = LoginForm()
    login.show()

    

    sys.exit(app.exec())
