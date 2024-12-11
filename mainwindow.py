from PyQt6.QtWidgets import QApplication, QMainWindow, QMessageBox, QTableWidgetItem, QGraphicsScene
from PyQt6.QtGui import QPainter, QPen, QPolygonF, QBrush, QFont
from PyQt6 import uic
from PyQt6.QtCore import Qt, QPointF
from User import User
from Dialogs import Login, Register, CreateTable, AddData, Key, UpdateData
import mysql.connector
from graph import Graph
import math
import random

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        uic.loadUi('ui/mainwindow.ui', self)

        self.setFixedSize(self.size())

        self.__user: User = User()
        self.__displayed_table: str = ''
            
        self.displayed_table = ''

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

        self.conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='codeleee{123}',
            database=self.__user.get_username()
        )
        self.cursor = self.conn.cursor()

        self.createTableBtn.clicked.connect(self.create_table)
        self.deleteTableBtn.clicked.connect(self.delete_table)
        self.addOnTable.clicked.connect(self.add_on_table)
        self.updateOnTable.clicked.connect(self.update_table)
        self.deleteFromTable.clicked.connect(self.delete_from_table)
        self.displayBtn.clicked.connect(self.diplayTable)
        self.runQuery.clicked.connect(self.run_query)
        self.refreshBtn.clicked.connect(self.generate_sample_schema)

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

        self.terminal.append("Welcome to ADEMY")

    def generate_sample_schema(self):
        """Generate a schema with a more natural, flowchart-like layout."""

        self.graph = Graph(self.__user, self.cursor).get_graph_data()

        self.scene.clear()  # Clear existing items
        table_positions = {}
        x_offset, y_offset = 50, 50
        layer_spacing = 200  # Vertical spacing between layers
        node_spacing = 250   # Horizontal spacing between nodes in the same layer
        random_offset = 50   # Maximum random offset for positioning
        
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
                # Apply horizontal and vertical spacing with randomness for a more organic look
                x = x_start + idx * node_spacing + random.randint(-random_offset, random_offset)
                y += random.randint(-random_offset // 2, random_offset // 2)  # Slight vertical randomness
                table_positions[table] = (x, y)

        # Add all tables to the scene
        for table_name, (x, y) in table_positions.items():
            self.add_table(table_name, x, y)

        # Add relationships with arrows
        all_nodes = set(self.graph.keys()).union(*self.graph.values())
        processed = set()
        for node in all_nodes:
            if node not in table_positions:
                x = random.randint(50, 500)  # Assign random X
                y = random.randint(50, 500)  # Assign random Y
                table_positions[node] = (x, y)
                self.add_table(node, x, y)

        for table, children in self.graph.items():
            x1, y1 = table_positions[table]
            for child in children:
                x2, y2 = table_positions[child]
                self.add_relationship_with_arrow(x1, y1, x2, y2)


    def add_table(self, name, x, y):
        """Add a table node to the scene."""
        rect_width, rect_height = 150, 100
        rect = self.scene.addRect(x, y, rect_width, rect_height, QPen(Qt.GlobalColor.black), QBrush(Qt.GlobalColor.lightGray))
        text = self.scene.addText(name)
        text.setFont(QFont('Segoe UI', 12))
        text.setPos(x + 10, y + 10)
        return rect

    def add_relationship_with_arrow(self, x1, y1, x2, y2):
        """Add an arrow between two tables."""
        line = self.scene.addLine(x1 + 75, y1 + 50, x2 + 75, y2 + 50, QPen(Qt.GlobalColor.blue, 2))
        line.setZValue(0)  # Place the arrows behind the tables

        # Calculate the angle of the arrow
        angle = math.atan2(y2 - y1, x2 - x1)
        arrow_size = 10

        # Points for the arrowhead
        arrow_p1 = QPointF(
            x2 + 75 - arrow_size * math.cos(angle - math.pi / 6),
            y2 + 50 - arrow_size * math.sin(angle - math.pi / 6),
        )
        arrow_p2 = QPointF(
            x2 + 75 - arrow_size * math.cos(angle + math.pi / 6),
            y2 + 50 - arrow_size * math.sin(angle + math.pi / 6),
        )

        # Create the arrowheads
        self.scene.addLine(x2 + 75, y2 + 50, arrow_p1.x(), arrow_p1.y(), QPen(Qt.GlobalColor.blue, 2)).setZValue(0)
        self.scene.addLine(x2 + 75, y2 + 50, arrow_p2.x(), arrow_p2.y(), QPen(Qt.GlobalColor.blue, 2)).setZValue(0)

    def delete_table(self):
        table = self.listWidget.currentItem().text() if self.listWidget.currentItem() is not None else ''

        if table == '':
            self.terminal.append("Please select a table to delete")
            return
        
        response = QMessageBox.question(self, 'Delete Table', 'Are you sure you want to delete the table?', QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if response is not QMessageBox.StandardButton.Yes:
            return

        strongly_connected = Graph(self.__user, self.cursor).kosaraju()

        for component in strongly_connected:
            if table in component and len(component) > 1:
                self.terminal.append("Cannot delete table with foreign key constraint")
                return

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
        
        if dialog.tableWidget.rowCount() == 0:
            self.terminal.append("Table must have at least one column")
            return
            
        foreign_keys = ""
        query = f"CREATE TABLE {dialog.tableName.text()} ("

        for i in range(dialog.tableWidget.rowCount()):
            
            if dialog.tableWidget.item(i, 0) is None or dialog.tableWidget.item(i, 1) is None:
                self.terminal.append("Column name and data type cannot be empty")
                return
            
            query = query + f"{dialog.tableWidget.item(i, 0).text()}, "

            if dialog.tableWidget.item(i, 1) is None:
                self.terminal.append("Data type cannot be empty")
                return

            query = query[:-2] + f" {dialog.tableWidget.item(i, 1).text()}, "

            if dialog.tableWidget.item(i, 2) is not None:
                
                if dialog.tableWidget.item(i, 2).text() =='P' or dialog.tableWidget.item(i, 2).text() == 'p':
                    query = query[:-2] +  ' PRIMARY KEY, '
                elif ',' in dialog.tableWidget.item(i, 2).text():
                    ref = dialog.tableWidget.item(i, 2).text().replace(" ", '').split(',')
                    
                    if len(ref) != 2:
                        self.terminal.append("Invalid foreign key")
                        return
                    
                    foreign_keys += f" FOREIGN KEY ({dialog.tableWidget.item(i, 0).text()}) REFERENCES {ref[0]}({ref[1]}), "
                elif dialog.tableWidget.item(i, 2).text().replace(' ','') == '':
                    pass
                else:
                    self.terminal.append("Invalid key")
                    return
                
            if dialog.tableWidget.item(i, 3) is not None:

                if dialog.tableWidget.item(i, 3).text() == 'U' or dialog.tableWidget.item(i, 3).text() == 'u':
                    query = query[:-2] + ' UNIQUE, '
                
                else:
                    self.terminal.append("Invalid constraint")
                    return
                
            if dialog.tableWidget.item(i, 4) is not None:
                
                if dialog.tableWidget.item(i, 4).text() == 'N' or dialog.tableWidget.item(i, 4).text() == 'n':
                    query = query[:-2] + ' NOT NULL, '
                
                else:
                    self.terminal.append("Invalid constraint")
                    return
            
            query = query[:-2] + ', '

        query = query[:-2] + ', ' + foreign_keys 
        query = query[:-2] + ')'

        if 'primary key' not in query.lower():
            self.terminal.append("Primary key is required")
            return
        
        if query.lower().count('primary key') > 1:
            self.terminal.append("Only one primary key is allowed")
            return
            
        print(query)
        try:
            self.cursor.execute(query)
            self.conn.commit()
            self.terminal.append(f"{dialog.tableName.text()} created successfully")
        except Exception as e:
            self.terminal.append("Table creation failed")
            self.terminal.append("Error: " + str(e))

        self.listWidget.clear()
        self.diplayTables()
        
    def diplayTables(self):

        self.cursor.execute("SHOW TABLES")
        tables = self.cursor.fetchall()

        for table in tables:
            self.listWidget.addItem(table[0])
        
        self.terminal.append("Tables loaded tp table list")

    def add_on_table(self):
        table = self.listWidget.currentItem().text() if self.listWidget.currentItem() is not None else ''
        
        if table == '':
            return

        dialog = AddData(table, self.cursor)
        dialog.exec()

        if dialog.result() != 1:
            return

        for i in range(dialog.tableWidget.rowCount()):
            query = f"INSERT INTO {table} VALUES ("

            try:
                for j in range(dialog.tableWidget.columnCount()):
                    query += f"'{dialog.tableWidget.item(i, j).text()}', "
            except Exception as e:
                self.terminal.append("Invalid data")
                return
            
            query = query[:-2] + ')'

            try:
                self.cursor.execute(query)
                self.conn.commit()
                self.terminal.append("Row added successfully")
            except Exception as e:
                self.terminal.append(str(e))

        self.conn.commit()

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
        
        # get primary key
        self.cursor.execute("SHOW KEYS FROM {} WHERE Key_name = 'PRIMARY'".format(table))
        primary_key = self.cursor.fetchall()[0][4]

        self.cursor.execute(f"SELECT * FROM {table} WHERE {primary_key} = '{key.getKey()}'")
        data = self.cursor.fetchall()

        if len(data) == 0:
            self.terminal.append("Data not found")
            return
        
        # get columns names
        self.cursor.execute(f"""
                            SELECT COLUMN_NAME 
                            FROM information_schema.COLUMNS 
                            WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s""" , (self.__user.get_username(), table))
        columns = self.cursor.fetchall()

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
            query += f"{columns[i][0]} = '{new_data[i]}'"
            if i != len(columns) - 1:
                query += ", "

        query += f" WHERE {primary_key} = '{key.key.text()}'"

        print(query)

        try:
            self.cursor.execute(query)
            self.conn.commit()
        except Exception as e:
            self.terminal.append("Update failed : " + str(e))
            return

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
        
        # get primary key
        self.cursor.execute("SHOW KEYS FROM {} WHERE Key_name = 'PRIMARY'".format(table))

        primary_key = self.cursor.fetchall()[0][4]

        try:
            self.cursor.execute(f"DELETE FROM {table} WHERE {primary_key} = '{key.getKey()}'")
            self.conn.commit()
            self.terminal.append("Data deleted successfully")
        except Exception as e:
            self.terminal.append(str(e))

    def diplayTable(self):
        table = self.listWidget.currentItem().text() if self.listWidget.currentItem() is not None else ''

        if table == '':
            return

        self.cursor.execute(f"SELECT * FROM {table}")
        data = self.cursor.fetchall()

        if len(data) == 0:
            self.terminal.append("No data found")
            return

        self.tableContent.clear()
        self.tableContent.setColumnCount(len(data[0]))
        self.tableContent.setRowCount(len(data))

        for i in range(len(data[0])):
            self.tableContent.setHorizontalHeaderItem(i, QTableWidgetItem(self.cursor.description[i][0]))

        for i in range(len(data)):
            for j in range(len(data[0])):
                item = QTableWidgetItem(str(data[i][j]))
                item.setFont(QFont('Arial', 12))  # Set font and size
                item.setForeground(Qt.GlobalColor.white)  # Set text color
                self.tableContent.setItem(i, j, item)

        self.tableContent.resizeColumnsToContents()
    
    def run_query(self):
        query = self.queryEditor.toPlainText()
        
        if query == '':
            self.terminal.append("Query cannot be empty")
            return
        
        if 'database' in query.lower():
            self.terminal.append("You cannot create/drop database")
            return

        if 'create table' in query.lower() and 'primary key' not in query.lower():
            self.terminal.append("Primary key is required")
            return
        
        if len(query) == 3 and query.lower() == 'cls':
            self.terminal.clear()
            return
        

        try:
            if 'select' in query.lower():
                self.cursor.execute(query)
                data = self.cursor.fetchall()
                
                table_name = query.split(' ')[query.split(' ').index('from') + 1]

                self.tableContent.clear()
                self.tableContent.setColumnCount(len(data[0]))
                self.tableContent.setRowCount(len(data))

                for i in range(len(data[0])):
                    self.tableContent.setHorizontalHeaderItem(i, QTableWidgetItem(self.cursor.description[i][0]))

                for i in range(len(data)):
                    for j in range(len(data[0])):
                        self.tableContent.setItem(i, j, QTableWidgetItem(str(data[i][j])))

                self.tableContent.resizeColumnsToContents()
                self.__displayed_table = table_name

            else:
                self.cursor.execute(query)
                self.conn.commit()
            
            self.terminal.append("Query executed successfully")

        except Exception as e:
            self.terminal.append(str(e))

    

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
