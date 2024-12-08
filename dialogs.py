from PyQt6.QtWidgets import QDialog, QMessageBox
from PyQt6 import uic
import sys
import sqlite3

class Login(QDialog):
    def __init__(self):
        super(Login, self).__init__()
        uic.loadUi('ui/loginform.ui', self)
    
        self.loginbtn.clicked.connect(self.login)
        self.newuserbtn.clicked.connect(self.new_user)
    
    def login(self):

        uname = self.username.text()
        passwd = self.password.text()

        conn = sqlite3.connect('databases/users.db')
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', (uname, passwd))
        user = cursor.fetchone()

        conn.close()

        if user is None:
            QMessageBox.warning(self, 'Error', 'Invalid username or password')
            return

        self.accept()
        self.close()

    def new_user(self):
        self.reject()
        self.close()
    
    def closeEvent(self, event):
        sys.exit()

class Register(QDialog):
    def __init__(self):
        super(Register, self).__init__()
        uic.loadUi('ui/signup.ui', self)
    
        self.registerbtn.clicked.connect(self.register)
        self.cancelbtn.clicked.connect(self.cancel)
    
    def register(self):
        uname = self.username.text()
        passwd = self.password.text()
        repasswd = self.repassword.text()

        if uname == '' or passwd == '' or repasswd == '':
            QMessageBox.warning(self, 'Error', 'Please fill all fields')
            return
        
        if passwd != repasswd:
            QMessageBox.warning(self, 'Error', 'Passwords do not match')
            return
        
        if uname == 'users':
            QMessageBox.warning(self, 'Error', 'Invalid username')
            return

        conn = sqlite3.connect('databases/users.db')
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM users WHERE username = ?', (uname,))

        if cursor.fetchone() is not None:
            QMessageBox.warning(self, 'Error', 'Username already exists')
            conn.close()
            return
        
        cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (uname, passwd))
        conn.commit()
        conn.close()

        conn = sqlite3.connect('databases/{}.db'.format(uname))
        conn.commit()
        conn.close()

        self.accept()
        self.close()

    def cancel(self):
        self.reject()
        self.close()
    
    def closeEvent(self, event):
        self.reject()
        self.close()