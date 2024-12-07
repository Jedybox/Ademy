from PyQt6.QtWidgets import QApplication, QDialog, QMessageBox
from PyQt6 import uic
import sys
import sqlite3


class LoginForm(QDialog):

    def __init__(self):
        super(LoginForm, self).__init__()
        uic.loadUi("ui/loginform.ui", self)

        self.loginbtn.clicked.connect(self.login)
        self.newuserbtn.clicked.connect(self.newuser)

        self.__username = None
        self.__password = None
    
    def login(self):
        self.__username = self.username.text()
        self.__password = self.password.text()

        conn = sqlite3.connect("databases/users.db")
        cursor = conn.cursor()

        cursor.execute(""" 
            SELECT * FROM users WHERE username = ? AND password = ?;
        """, (self.__username, self.__password))
        
        user = cursor.fetchone()
        conn.close()

        if user is None:
            QMessageBox.critical(self, "Error", "Invalid username or password")
            self.__username = None
            self.__password = None
            return

        self.hide()
    
    def newuser(self):
        # Hide the login form
        self.hide()

        # Clear any existing text in username and password fields
        self.username.clear()
        self.password.clear()

        # Create and show the register form
        register = RegisterForm(self)
        register.exec()  # Block until the user finishes registration

        # Show login form after registration or cancel
        self.show()
    
    def get_username(self):
        return self.__username
    
    def get_password(self):
        return self.__password
    
    def closeEvent(self, event):
        QApplication.quit()  # Use quit instead of sys.exit(0)


class RegisterForm(QDialog):

    def __init__(self, parent: LoginForm):
        super().__init__()
        uic.loadUi("ui/signup.ui", self)

        self.__parent = parent
        self.registerbtn.clicked.connect(self.register)
        self.cancelbtn.clicked.connect(self.cancel)
    
    def register(self):
        username = self.username.text()
        password = self.password.text()
        repassword = self.repassword.text()

        if username == "" or password == "" or repassword == "":
            QMessageBox.critical(self, "Error", "Username and passwords must not be empty")
            return
        
        if password != repassword:
            QMessageBox.critical(self, "Error", "Passwords do not match")
            return

        conn = sqlite3.connect("databases/users.db")
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO users (username, password) VALUES (?, ?);
        """, (username, password))
        
        conn.commit()
        conn.close()

        self.__parent.show()  # Show the parent dialog again
        self.close()  # Close the register dialog
    
    def cancel(self):
        self.__parent.show()  # Show the parent dialog again
        self.close()  # Close the register dialog
    
    def closeEvent(self, event):
        self.__parent.show()  # Ensure the parent dialog is visible
        self.close()  # Close the register dialog
