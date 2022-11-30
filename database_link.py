import psycopg2
from variables import database_name, database_user
import logging
from variables import data_path, sed_name
import os


class DatabaseLink:
    def __init__(self):
        self.conn = psycopg2.connect(database=database_name, user=database_user)
        self.cursor = self.conn.cursor()
        self.tables = ['archive', 'pushevent', 'commit', 'commitcommentevent', 'releaseevent', 'deleteevent',
                       'gollumevent']

    def __enter__(self):
        self.__init__()
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.conn.commit()
        self.cursor.close()
        self.conn.close()

    def create_tables(self):
        with open('sql/create_tables.sql', 'r') as f:
            self.cursor.execute(f.read())

    def add_primary_keys(self):
        with open('sql/primary_keys.sql', 'r') as f:
            self.cursor.execute(f.read())

    def insert_csvs_into_db(self):
        for table in self.tables:
            query = f"COPY {table} FROM '{data_path}/{table}.csv' WITH (FORMAT csv)"
            try:
                self.cursor.execute(query)
            except psycopg2.errors.CharacterNotInRepertoire:
                logging.error(f'Error in table {table}, removing null bytes')
                self.conn.rollback()
                os.system(f"{sed_name} -i 's/\\x00//g' {data_path}/{table}.csv")
                self.cursor.execute(query)
            self.conn.commit()
            logging.info(f'Inserted {table} into database')
