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

class CreateTable(QDialog):
    
    def __init__(self, user):
        super(CreateTable, self).__init__()
        uic.loadUi('ui/crearetable.ui', self)
        
        self.__user = user

        self.createbtn.clicked.connect(self.create)
        self.cancelbtn.clicked.connect(self.cancel)
        self.addbtn.clicked.connect(self.add)
        self.minusbtn.clicked.connect(self.minus)
    
    def create(self):
        conn = sqlite3.connect('databases/{}.db'.format(self.__user.get_username()))
        cursor = conn.cursor()

        table_name = self.tableName.text()

        # Check if table name is empty
        if table_name == '':
            QMessageBox.warning(self, 'Error', 'Please specify a table name')
            return
        
        # Check if table name is valid
        cursor.execute('SELECT name FROM sqlite_master WHERE type = "table" AND name = ?', (table_name,))
        if cursor.fetchone() is not None:
            QMessageBox.warning(self, 'Error', 'Table already exists')
            return

        # Check if there are no columns
        if self.table.rowCount() == 0:
            QMessageBox.warning(self, 'Error', 'Please add columns')
            return

        # Check if there are empty column names
        for i in range(self.table.rowCount()):
            if self.table.item(i, 0) is None:
                QMessageBox.warning(self, 'Error', 'Please fill all column names')
                return
        
        # Check if there are empty column types
        for i in range(self.table.rowCount()):
            if self.table.item(i, 1) is None:
                QMessageBox.warning(self, 'Error', 'Please fill all column types')
                return
        
        # Check if there are duplicate column names
        column_names = []
        for i in range(self.table.rowCount()):
            if self.table.item(i, 0).text() in column_names:
                QMessageBox.warning(self, 'Error', 'Duplicate column names')
                return
            column_names.append(self.table.item(i, 0).text())
        
        # Check if there is only one primary key
        primary_keys = 0
        for i in range(self.table.rowCount()):
            
            if self.table.item(i, 2) is None:
                continue

            if self.table.item(i, 2).text() == 'P' or self.table.item(i, 2).text() == 'p':
                primary_keys += 1
            if primary_keys > 1:
                QMessageBox.warning(self, 'Error', 'Only one primary key is allowed')
                return

        # Check if there are no primary keys
        if primary_keys == 0:
            QMessageBox.warning(self, 'Error', 'Please specify a primary key')
            return
        
        # Create table
        query = """
        CREATE TABLE {} (
        """.format(table_name)
        foriegn_key = []

        for i in range(self.table.rowCount()):
            name_ = self.table.item(i, 0).text()
            type_ = self.table.item(i, 1).text()
            keyType = self.table.item(i, 2).text() if self.table.item(i, 2) is not None else ''
            
            if keyType == 'P' or keyType == 'p':
                keyType = 'PRIMARY KEY'
            elif ',' in keyType:
                
                if keyType.count(',') > 1:
                    QMessageBox.warning(self, 'Error', 'Foreign key input error')
                    return
                
                keyType = keyType.replace(' ', '')
                
                foriegn_key = keyType.split(',')
                foriegn_key.append(name_)

            query += '{} {} {},\n'.format(name_, type_, keyType)
        
        if foriegn_key:
            query += 'FOREIGN KEY ({}) REFERENCES {}({}),\n'.format(
                foriegn_key[2], foriegn_key[0], foriegn_key[1]
            )
        
        query = query[:-2] + ');'

        cursor.execute(query)
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
    
    def add(self):
        self.table.insertRow(self.table.rowCount())
    
    def minus(self):
        self.table.removeRow(self.table.rowCount() - 1)
