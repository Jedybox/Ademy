from PyQt6.QtWidgets import QApplication, QMainWindow, QMessageBox, QTableWidgetItem, QGraphicsScene
from PyQt6.QtGui import QPainter, QPen, QPolygonF, QBrush
from PyQt6 import uic
from PyQt6.QtCore import Qt, QPointF
from User import User
from Dialogs import Login, Register, CreateTable, AddData, Key, UpdateData
import sqlite3
from graph import Graph
import math

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

        self.scene = QGraphicsScene()
        self.graphicsView.setScene(self.scene)
        self.graphicsView.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.generate_sample_schema()

        #centering the window
        screen = QApplication.primaryScreen()
        screen_geometry = screen.availableGeometry()
        window_geometry = self.frameGeometry()
        window_geometry.moveCenter(screen_geometry.center())
        self.move(window_geometry.topLeft())
        self.show()

        self.terminal.append("Welcome to SQLite ADEMY")

    def generate_sample_schema(self):
        """Generate a schema with a flowchart layout."""
        self.scene.clear()  # Clear existing items
        self.graph = Graph(self.__user).get_graph_data()

        # Use a dictionary to keep track of node positions
        table_positions = {}
        x_offset, y_offset = 50, 50
        layer_spacing = 300  # Increased vertical spacing between layers
        node_spacing = 250   # Increased horizontal spacing between nodes in the same layer

        # Calculate positions using a flowchart style
        processed = set()
        layers = []

        # Recursive function to create layers
        def assign_layer(table, current_layer):
            if table in processed:
                return
            if len(layers) <= current_layer:
                layers.append([])
            layers[current_layer].append(table)
            processed.add(table)
            for child in self.graph.get(table, []):
                assign_layer(child, current_layer + 1)

        # Start with all root nodes (tables with no incoming edges)
        root_nodes = set(self.graph.keys()) - {edge for edges in self.graph.values() for edge in edges}
        for root in root_nodes:
            assign_layer(root, 0)

        # Assign positions based on layers
        for layer_idx, layer in enumerate(layers):
            x_start = x_offset
            y = y_offset + layer_idx * layer_spacing
            for idx, table in enumerate(layer):
                x = x_start + idx * node_spacing
                table_positions[table] = (x, y)

        # Add all tables to the scene
        for table_name, (x, y) in table_positions.items():
            self.add_table(table_name, x, y)

        # Add relationships with arrows
        for table_name, edges in self.graph.items():
            from_x, from_y = table_positions[table_name]
            for edge in edges:
                if edge in table_positions:
                    to_x, to_y = table_positions[edge]
                    self.add_relationship_with_arrow(from_x, from_y, to_x, to_y)


    def add_table(self, name, x, y):
        """Add a table node to the scene."""
        rect = self.scene.addRect(x, y, 150, 100, QPen(Qt.GlobalColor.black), Qt.GlobalColor.lightGray)
        text = self.scene.addText(name)
        text.setPos(x + 10, y + 10)
        return rect

    def add_relationship_with_arrow(self, x1, y1, x2, y2):
        """Add a relationship line with an arrow between tables."""
        # Offset for the center of the rectangles
        start_x = x1 + 75
        start_y = y1 + 50
        end_x = x2 + 75
        end_y = y2

        # Draw line
        self.scene.addLine(start_x, start_y, end_x, end_y, QPen(Qt.GlobalColor.blue))

        # Add arrowhead
        arrow_size = 10
        angle = math.atan2(end_y - start_y, end_x - start_x)

        # Define arrow points
        arrow_p1 = QPointF(end_x - arrow_size * math.cos(angle - math.pi / 6),
                           end_y - arrow_size * math.sin(angle - math.pi / 6))
        arrow_p2 = QPointF(end_x - arrow_size * math.cos(angle + math.pi / 6),
                           end_y - arrow_size * math.sin(angle + math.pi / 6))

        arrow_head = QPolygonF([QPointF(end_x, end_y), arrow_p1, arrow_p2])
        self.scene.addPolygon(arrow_head, QPen(Qt.GlobalColor.blue), QBrush(Qt.GlobalColor.blue))

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

        if dialog.result() != 1:
            return

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
