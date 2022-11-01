import psycopg
import json
from variables import database_name, database_user

class DatabaseLink:
    def __enter__(self):
        self.conn = psycopg.connect(f'dbname={database_name} user={database_user}')
        self.cursor = self.conn.cursor()
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.conn.commit()
        self.cursor.close()
        self.conn.close()


    def createTable(self, date_string):
        # TODO specify varchar length
        self.cursor.execute(f'CREATE TABLE IF NOT EXISTS "{date_string}" \
            (id bigint NOT NULL PRIMARY KEY, \
            type varchar);')

    def insert_json(self, data):
        entry = json.loads(data[0])
        date = entry['created_at']
        date_string = date[:13].replace('T', '-')

        self.createTable(date_string)

        for entry in data:
            entry = json.loads(entry)
            
            self.cursor.execute(f'INSERT INTO "{date_string}" (id, type) \
                VALUES (%s, %s) ON CONFLICT DO NOTHING', (entry['id'], entry['type']))
            
