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
        self.__displayed_table: str = ''

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
        self.runQuery.clicked.connect(self.run_query)
        self.applyChangesBtn.clicked.connect(self.apply_changes)

        self.diplayTables()

        self.show()

        self.terminal.append("Welcome to SQLite ADEMY")

    def delete_table(self):
        table = self.listWidget.currentItem().text() if self.listWidget.currentItem() is not None else ''

        if table == '':
            self.terminal.append("Please select a table to delete")
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

        conn = sqlite3.connect('databases/{}.db'.format(self.__user.get_username()))
        cursor = conn.cursor()

        table_name = dialog.tableName.text()

        # Check if table name is empty
        if table_name.strip() == '':
            self.terminal.append("Table name cannot be empty")
            return
        
        # Check if table name is valid
        cursor.execute('SELECT name FROM sqlite_master WHERE type = "table" AND name = ?', (table_name,))
        if cursor.fetchone() is not None:
            self.terminal.append("Table already exists")
            return

        # Check if there are no columns
        if dialog.table.rowCount() == 0:
            self.terminal.append("Please add columns")
            return

        # Check if there are empty column names
        for i in range(dialog.table.rowCount()):
            if dialog.table.item(i, 0) is None:
                self.terminal.append("Please fill all column names")
                return
        
        # Check if there are empty column types
        for i in range(dialog.table.rowCount()):
            if dialog.table.item(i, 1) is None:
                self.terminal.append("Please fill all column types")
                return
        
        # Check if there are duplicate column names
        column_names = []
        for i in range(dialog.table.rowCount()):
            if dialog.table.item(i, 0).text() in column_names:
                self.terminal.append("Duplicate column names are not allowed")
                return
            column_names.append(dialog.table.item(i, 0).text())
        
        # Check if there is only one primary key
        primary_keys = 0
        for i in range(dialog.table.rowCount()):
            
            if dialog.table.item(i, 2) is None:
                continue

            if dialog.table.item(i, 2).text() == 'P' or dialog.table.item(i, 2).text() == 'p':
                primary_keys += 1
            if primary_keys > 1:
                self.terminal.append("Only one primary key is allowed")
                return

        # Check if there are no primary keys
        if primary_keys == 0:
            self.terminal.append("Please specify a primary key")
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
                    self.terminal.append("Error. Foreign key input error.")
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

        conn = sqlite3.connect('databases/{}.db'.format(self.__user.get_username()))
        cursor = conn.cursor()

        query = 'INSERT INTO {} VALUES ('.format(self.__table)
        for i in range(self.tableWidget.columnCount()):
            query += '?, '.format(self.tableWidget.item(0, i).text())

            
        query = query[:-2] + ')'

        for i in range(self.tableWidget.rowCount()):
            values = []
            for j in range(self.tableWidget.columnCount()):
                values.append(self.tableWidget.item(i, j).text())
            
            try:
                cursor.execute(query, values)
            except Exception as e:
                self.terminal.append(str(e))

        conn.commit()
        conn.close()

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

        self.__table = table

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
    
    def run_query(self):
        query = self.queryEditor.toPlainText()
        
        if query == '':
            self.terminal.append("Query cannot be empty")
            return
        
        if 'database' in query.lower():
            self.terminal.append("You cannot create/drop database")
            return
        
        conn = sqlite3.connect('databases/{}.db'.format(self.__user.get_username()))
        cursor = conn.cursor()

        try:
            cursor.execute(query)
            conn.commit()
            self.terminal.append("Query executed successfully")
        except Exception as e:
            self.terminal.append(str(e))

        conn.close()

        self.listWidget.clear()
        self.diplayTables()

    def apply_changes(self):

        if self.__displayed_table == '':
            return

        conn = sqlite3.connect('databases/{}.db'.format(self.__user.get_username()))
        cursor = conn.cursor()

        cursor.execute("Delete * from {}".format(self.__displayed_table))
        conn.commit()

        for i in range(self.tableContent.rowCount()):
            query = f"INSERT INTO {self.__displayed_table} VALUES ("
            for j in range(self.tableContent.columnCount()):
                query += f"'{self.tableContent.item(i, j).text()}', "
            
            query = query[:-2] + ')'

            try:
                cursor.execute(query)
                conn.commit()
                self.terminal.append("Row added successfully")
            except Exception as e:
                self.terminal.append(str(e))

        conn.close()

        self.terminal.append("Changes applied successfully")
