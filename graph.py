from User import User
import sqlite3

class Graph:

    def __init__(self, user: User) -> None:
        self.graph = {}
        self.tables = {}
        self.user = user

        conn = sqlite3.connect(f"databases/{self.user.get_username()}.db")
        cursor = conn.cursor()

        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()

        for table_name in tables:
            table_name = table_name[0]
            columns = []
            edges = []

            # List columns and primary keys
            cursor.execute(f"PRAGMA table_info('{table_name}');")
            for column in cursor.fetchall():
                col_id, name, data_type, notnull, default, pk = column
                columns.append(f"  - {name} ({data_type}) {'NOT NULL' if notnull else ''} {'PRIMARY KEY' if pk else ''}")
            
            # List foreign keys
            cursor.execute(f"PRAGMA foreign_key_list('{table_name}');")
            for fk in cursor.fetchall():
                _, _, ref_table, from_col, to_col, on_update, on_delete, _ = fk
                edges.append(f'{ref_table}')
            
            self.tables[table_name] = columns
            self.graph[table_name] = edges

        conn.close()

        print(self.graph)
    
        for links in self.kosaraju():
            print(links)
    
    def kosaraju(self):
        stack = []
        visited = set()

        def fill_order(v):
            visited.add(v)
            if v in self.graph:
                for neighbor in self.graph[v]:
                    if neighbor not in visited:
                        fill_order(neighbor)
            stack.append(v)

        def dfs(v, transposed_graph, visited):
            visited.add(v)
            component = [v]
            if v in transposed_graph:
                for neighbor in transposed_graph[v]:
                    if neighbor not in visited:
                        component.extend(dfs(neighbor, transposed_graph, visited))
            return component

        for node in self.graph:
            if node not in visited:
                fill_order(node)

        transposed_graph = {}
        for node in self.graph:
            for neighbor in self.graph[node]:
                if neighbor not in transposed_graph:
                    transposed_graph[neighbor] = []
                transposed_graph[neighbor].append(node)

        visited.clear()
        strongly_connected_components = []

        while stack:
            node = stack.pop()
            if node not in visited:
                component = dfs(node, transposed_graph, visited)
                strongly_connected_components.append(component)

        return strongly_connected_components

    def get_graph_data(self):
        return self.graph
