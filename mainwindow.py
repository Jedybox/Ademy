from PyQt6.QtWidgets import QMainWindow, QMessageBox
from PyQt6 import uic
from PyQt6.QtCore import Qt
from User import User
from Dialogs import Login, Register, CreateTable
import sqlite3

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        uic.loadUi('ui/mainwindow.ui', self)

        self.setFixedSize(self.size())

        self.__user: User = User()

        while True:
            login: Login = Login()
            login.exec()

            print("Logged in" if login.result() == 1 else "Registering") # Debugging

            if login.result() == 1:
                self.__user.set_username(login.username.text())
                self.__user.set_password(login.password.text())
                break
            else:
                register = Register()
                register.exec()
        
        self.createTableBtn.clicked.connect(self.create_table)
        self.deleteTableBtn.clicked.connect(self.delete_table)

        self.diplayTables()

        self.show()

    def delete_table(self):
        table = self.listWidget.currentItem().text() if self.listWidget.currentItem() is not None else ''

        if table == '':
            QMessageBox.warning(self, 'Error', 'Please select a table to delete')
            return
        
        response = QMessageBox.question(self, 'Delete Table', 'Are you sure you want to delete the table?', QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if response is not QMessageBox.StandardButton.Yes:
            return

        conn = sqlite3.connect('databases/{}.db'.format(self.__user.get_username()))
        cursor = conn.cursor()

        cursor.execute("DROP TABLE {}".format(table))
        conn.commit()

        conn.close()

        self.listWidget.takeItem(self.listWidget.currentRow())
        self.terminal.append(f"Table {table} is deleted")

    def create_table(self):

        dialog = CreateTable(self.__user)
        dialog.exec()

        if dialog.result() == 1:
            self.terminal.append("Table created successfully")
            self.listWidget.addItem(dialog.tableName.text())
        
    def diplayTables(self):
        conn = sqlite3.connect('databases/{}.db'.format(self.__user.get_username()))
        cursor = conn.cursor()

        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()

        for table in tables:
            self.listWidget.addItem(table[0])
            print(table[0])

        conn.close()
        