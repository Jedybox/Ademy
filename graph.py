from User import User
import mysql.connector

class Graph:

    def __init__(self, user: User, cursor: mysql.connector.cursor.MySQLCursor) -> None:
        self.graph = {}
        self.user = user

        # get all tables
        cursor.execute("""
                       SHOW TABLES 
                       """)
        
        fetched_tables = cursor.fetchall()

        for table in fetched_tables:
            selected_table = table[0]

            cursor.execute("""
                            SELECT COLUMN_NAME, REFERENCED_TABLE_NAME, REFERENCED_COLUMN_NAME
                            FROM information_schema.key_column_usage
                            WHERE TABLE_SCHEMA = %s
                            AND TABLE_NAME = %s
                            AND REFERENCED_TABLE_NAME IS NOT NULL
                            """, (user.get_username(), selected_table))

            fetched_foreign_keys = cursor.fetchall()

            if fetched_foreign_keys: print('has foreign keys: ', fetched_foreign_keys)

            foreign_ref_tables = []
            for foreign_key in fetched_foreign_keys:
                foreign_ref_tables.append(foreign_key[1])

            self.graph[selected_table] = foreign_ref_tables
        
        print(self.graph)
    
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
