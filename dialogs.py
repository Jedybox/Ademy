from PyQt6.QtWidgets import QDialog, QMessageBox, QTableWidgetItem
from PyQt6 import uic
from User import User
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

class AddData(QDialog):

    def __init__(self, user: User, table: str):
        super(AddData, self).__init__()
        uic.loadUi('ui/addData.ui', self)

        self.__user = user
        self.__table = table

        # get table columns
        conn = sqlite3.connect('databases/{}.db'.format(self.__user.get_username()))
        cursor = conn.cursor()

        cursor.execute('PRAGMA table_info({})'.format(self.__table))
        columns = cursor.fetchall()
        conn.close()

        # add columns to the table
        for column in columns:
            self.tableWidget.setColumnCount(self.tableWidget.columnCount() + 1)
            self.tableWidget.setHorizontalHeaderItem(self.tableWidget.columnCount() - 1, QTableWidgetItem(column[1]))
        
        self.addbtn.clicked.connect(self.add)
        self.minusbtn.clicked.connect(self.minus)
        self.addData.clicked.connect(self.add_data)
        self.cancelbtn.clicked.connect(self.cancel)
    
    def add(self):
        self.tableWidget.insertRow(self.tableWidget.rowCount())
    
    def minus(self):
        self.tableWidget.removeRow(self.tableWidget.rowCount() - 1)
    
    def add_data(self):
        
        self.accept()
        self.close()

    def cancel(self):
        self.reject()
        self.close()

class Key(QDialog):

    def __init__(self):
        super(Key, self).__init__()
        uic.loadUi('ui/keydata.ui', self)

        self.okbtn.clicked.connect(self.ok)
    
    def ok(self):
        self.accept()
        self.close()
    
    def getKey(self):
        return self.key.text()
    
class UpdateData(QDialog):

    def __init__(self, column, data):
        super(UpdateData, self).__init__()
        uic.loadUi('ui/updateData.ui', self)

        self.__columns = column
        self.__datas = data

        # set columns to table
        for i in range(len(self.__columns)):
            self.table.setColumnCount(self.table.columnCount() + 1)
            self.table.setHorizontalHeaderItem(self.table.columnCount() - 1, QTableWidgetItem(self.__columns[i][0]))
        
        # set data to table
        for i in range(len(self.__datas)):
            self.table.insertRow(self.table.rowCount())
            for j in range(len(self.__datas[i])):
                self.table.setItem(i, j, QTableWidgetItem(self.__datas[i][j]))
        
        self.updatebtn.clicked.connect(self.update)
        self.cancelbtn.clicked.connect(self.cancel)
    
    def update(self):
        self.accept()
        self.close()
    
    def cancel(self):
        self.reject()
        self.close()
    
    def get_data(self) -> list[str]:
        data = []
        for i in range(self.table.rowCount()):
            for j in range(self.table.columnCount()):
                data.append(self.table.item(i, j).text())

        return data
