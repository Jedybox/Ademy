from PyQt6.QtWidgets import QApplication, QMainWindow, QMessageBox, QTableWidgetItem, QGraphicsScene
from PyQt6.QtGui import QPainter
from PyQt6 import uic
from User import User
from Dialogs import Login, Register, CreateTable, AddData, Key, UpdateData
import sqlite3
from graph import Graph

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
        
        self.__graph: Graph = Graph(self.__user)

        self.createTableBtn.clicked.connect(self.create_table)
        self.deleteTableBtn.clicked.connect(self.delete_table)
        self.addOnTable.clicked.connect(self.add_on_table)
        self.updateOnTable.clicked.connect(self.update_table)
        self.deleteFromTable.clicked.connect(self.delete_from_table)
        self.displayBtn.clicked.connect(self.diplayTable)
        self.runQuery.clicked.connect(self.run_query)
        self.applyChangesBtn.clicked.connect(self.apply_changes)

        self.diplayTables()

        self.__scene = QGraphicsScene()
        self.graphicsView.setScene(self.__scene)
        self.graphicsView.setRenderHint(QPainter.RenderHint.Antialiasing)


        #centering the window
        screen = QApplication.primaryScreen()
        screen_geometry = screen.availableGeometry()
        window_geometry = self.frameGeometry()
        window_geometry.moveCenter(screen_geometry.center())
        self.move(window_geometry.topLeft())


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

        if dialog.result() == 0:
            return

        if dialog.tableName.text() == '':
            self.terminal.append("Invalid table name")
            return
        
        conn = sqlite3.connect('databases/{}.db'.format(self.__user.get_username()))
        cursor = conn.cursor()

        cursor.execute("PRAGMA foreign_keys = ON")

        query = f"""
                CREATE TABLE {dialog.tableName.text()} (
                """
        
        primary_key_count: int = 0
        foreign_keys = ""

        for i in range(dialog.table.rowCount()):
            query += "{} {}, ".format(dialog.table.item(i, 0).text(), dialog.table.item(i, 1).text())

            if dialog.table.item(i, 2) is None:
                pass
            elif dialog.table.item(i, 2).text() == 'P' or dialog.table.item(i, 2).text() == 'p':
                primary_key_count += 1
                query = query[:-2] +  " PRIMARY KEY, "
            elif ',' in dialog.table.item(i, 2).text():

                if len(dialog.table.item(i, 2).text().split(',')) != 2:
                    self.terminal.append("Invalid foreign key")
                    return
                
                foreign_keys += " FOREIGN KEY ({}) REFERENCES {}({}), ".format(
                    dialog.table.item(i, 0).text(), 
                    dialog.table.item(i, 2).text().split(',')[0], 
                    dialog.table.item(i, 2).text().split(',')[1])
            elif len(dialog.table.item(i, 2).text()) > 0:
                self.terminal.append("Invalid key type")
                return
            
            if dialog.table.item(i, 3) is None:
                pass
            elif dialog.table.item(i, 3).text() == 'U' or dialog.table.item(i, 3).text() == 'u':
                query = query[:-2] + " UNIQUE, "
            elif len(dialog.table.item(i, 3).text()) > 0:
                self.terminal.append("Invalid unique key")
                return
            
            if dialog.table.item(i, 4) is None:
                pass
            elif dialog.table.item(i, 4).text() == 'N' or dialog.table.item(i, 4).text() == 'n':
                query = query[:-2] + " NOT NULL, "
            elif len(dialog.table.item(i, 4).text()) > 0:
                self.terminal.append("Invalid not null key")
                return
            
        if primary_key_count > 1:
            self.terminal.append("Only one primary key is allowed")
            return

        if foreign_keys != "":
            query += foreign_keys

        query = query[:-2] + ")"

        print(query)

        try:
            cursor.execute(query)
            conn.commit()
            self.terminal.append(f"{dialog.tableName.text()} created successfully")
        except Exception as e:
            print(str(e))
            self.terminal.append("Table creation failed")
            self.terminal.append("This may be due to invalid data type or invalid foreign key")

        conn.close()

        self.listWidget.clear()
        self.diplayTables()
        
    def diplayTables(self):
        conn = sqlite3.connect('databases/{}.db'.format(self.__user.get_username()))
        cursor = conn.cursor()

        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()

        for table in tables:
            self.listWidget.addItem(table[0])

        conn.close()

    def add_on_table(self):
        table = self.listWidget.currentItem().text() if self.listWidget.currentItem() is not None else ''
        
        if table == '':
            return

        dialog = AddData(self.__user, table)
        dialog.exec()

        conn = sqlite3.connect('databases/{}.db'.format(self.__user.get_username()))
        cursor = conn.cursor()

        query = 'INSERT INTO {} VALUES ('.format(table)
        for i in range(dialog.tableWidget.columnCount()):
            query += '?, '.format(dialog.tableWidget.item(0, i).text())

            
        query = query[:-2] + ')'

        for i in range(dialog.tableWidget.rowCount()):
            values = []
            for j in range(dialog.tableWidget.columnCount()):
                values.append(dialog.tableWidget.item(i, j).text())
            
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

        if len(query) == 5 and query.lower() == 'clean':
            self.terminal.clear()
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
