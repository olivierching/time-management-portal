import sqlite3

class DBConnecter:
    def __init__(self, db_url):
        self.db_url = db_url
        self.connection = sqlite3.connect(db_url)
        self.cursor = self.connection.cursor()

    def open(self):
        self.connection = sqlite3.connect(self.db_url)
        self.cursor = self.connection.cursor()

    def close(self):
        self.connection.close()

    def execute_query(self, query, params=None):
        if params is None:
            params = ()
        self.cursor.execute(query, params)
        
        # Check if the query is a SELECT statement
        is_select = query.strip().upper().startswith('SELECT')
        
        if is_select:
            return self.cursor.fetchall()
        else:
            self.connection.commit()
            return None
