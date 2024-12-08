from PyQt6.QtWidgets import QMainWindow, QMessageBox, QTableWidgetItem
from PyQt6 import uic
from User import User
from Dialogs import Login, Register, CreateTable, AddData, Key, UpdateData
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
        self.addOnTable.clicked.connect(self.add_on_table)
        self.updateOnTable.clicked.connect(self.update_table)
        self.deleteFromTable.clicked.connect(self.delete_from_table)
        self.displayBtn.clicked.connect(self.diplayTable)

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

    def add_on_table(self):
        table = self.listWidget.currentItem().text() if self.listWidget.currentItem() is not None else ''
        
        if table == '':
            return

        dialog = AddData(self.__user, table)
        dialog.exec()

        if dialog.result() == 1:
            self.terminal.append("Data added successfully")

    def update_table(self):
        
        table = self.listWidget.currentItem().text() if self.listWidget.currentItem() is not None else ''

        if table == '':
            return

        key: Key = Key()
        key.exec()

        if key.result() == 0:
            return
        
        if key.getKey() == '':
            self.terminal.append("Key cannot be empty")
            return
        
        conn = sqlite3.connect('databases/{}.db'.format(self.__user.get_username()))
        cursor = conn.cursor()
        
        cursor.execute("PRAGMA table_info({})".format(table))
        columns = cursor.fetchall()

        ## get primary key
        primary_key = columns[0][1]
        print(primary_key)

        cursor.execute(f"SELECT * FROM {table} WHERE {primary_key} = '{key.key.text()}'")
        data = cursor.fetchall()

        if len(data) == 0:
            self.terminal.append("No data found for updates or key is invalid")

        datas = []
        for row in data:
            datas.append(row)
        

        dialog = UpdateData(columns, datas)
        dialog.exec()
    
        if dialog.result() != 1:
            self.terminal.append("Update cancelled")
            return
        
        new_data = [row for row in dialog.get_data()]

        query = f"UPDATE {table} SET "
        for i in range(len(columns)):
            query += f"{columns[i][1]} = '{new_data[i]}'"
            if i != len(columns) - 1:
                query += ", "

        query += f" WHERE {primary_key} = '{key.key.text()}'"

        cursor.execute(query)
        conn.commit()

        conn.close()

        self.terminal.append("Data updated successfully")
        
    def delete_from_table(self):
        table = self.listWidget.currentItem().text() if self.listWidget.currentItem() is not None else ''
        
        if table == '':
            return

        key: Key = Key()
        key.exec()

        if key.result() == 0:
            return
        
        if key.getKey() == '':
            self.terminal.append("Key cannot be empty")
            return
        
        conn = sqlite3.connect('databases/{}.db'.format(self.__user.get_username()))
        cursor = conn.cursor()

        cursor.execute("PRAGMA table_info({})".format(table))
        columns = cursor.fetchall()
        primary_key = columns[0][1]

        cursor.execute(f"SELECT * FROM {table} WHERE {primary_key} = '{key.getKey()}'")
        data = cursor.fetchall()

        if len(data) == 0:
            self.terminal.append("No data found for deletion or key is invalid")
            return

        cursor.execute(f"DELETE FROM {table} WHERE {primary_key} = '{key.getKey()}'")
        conn.commit()

        self.terminal.append("Data deleted successfully")

        conn.close()

    def diplayTable(self):
        table = self.listWidget.currentItem().text() if self.listWidget.currentItem() is not None else ''

        if table == '':
            return

        conn = sqlite3.connect('databases/{}.db'.format(self.__user.get_username()))
        cursor = conn.cursor()

        cursor.execute(f"SELECT * FROM {table}")
        data = cursor.fetchall()

        self.terminal.append(f"Displaying {table}")

        for row in data:
            self.terminal.append(str(row))
        
        self.terminal.append(f"{table} loaded successfully")

        cursor.execute("PRAGMA table_info({})".format(table))
        columns = cursor.fetchall()

        self.tableContent.clear()
        self.tableContent.setColumnCount(len(columns))
        self.tableContent.setRowCount(len(data))

        for i in range(len(columns)):
            self.tableContent.setHorizontalHeaderItem(i, QTableWidgetItem(columns[i][1]))
        
        for i in range(len(data)):
            for j in range(len(columns)):
                self.tableContent.setItem(i, j, QTableWidgetItem(str(data[i][j])))
        
        self.tableContent.resizeColumnsToContents()

        self.terminal.append("Table displayed successfully")

        conn.close()