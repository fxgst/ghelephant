import psycopg2
import os
import logging
import traceback
from variables import *
from csv_writers import CSVWriters
from psycopg2.errors import CharacterNotInRepertoire


class DatabaseLink:
    """
    Class to link to the database and perform operations on it.
    """
    def __init__(self):
        self.conn = psycopg2.connect(database=database_name, user=database_user,
            password=database_password, host=database_host, port=database_port)
        self.cursor = self.conn.cursor()

    def __enter__(self):
        self.__init__()
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.conn.commit()
        self.cursor.close()
        self.conn.close()

    def create_tables(self):
        """
        Create tables in the database.
        :return: None
        """
        with open('sql/create_tables.sql', 'r') as f:
            self.cursor.execute(f.read())
        self.conn.commit()

    def create_indices(self):
        """
        Create indices in the database.
        :return: None
        """
        logging.info('Creating indices')
        with open('sql/create_indices.sql', 'r') as f:
            self.cursor.execute(f.read())
        self.conn.commit()
        logging.info('Finished creating indices')

    def insert_csvs_into_db(self, date):
        """
        Insert CSV files into the database.
        :param date: the date of the files to be inserted, corresponds to file name
        :return: None
        """
        for table in CSVWriters.file_names:
            query = f"COPY {table} FROM '{data_path}/{table}-{date}.csv' WITH (FORMAT csv)"
            try:
                self.cursor.execute(query)
            except CharacterNotInRepertoire:
                self.conn.rollback()
                logging.warn(f'Illegal character in table {table} for {date}, removing null bytes and retrying')
                os.system(f"{sed_name} -i 's/\\x00//g' {data_path}/{table}-{date}.csv")
                logging.info(f'Removed null bytes from {table}')
                self.cursor.execute(query)
            except Exception:
                self.conn.rollback()
                logging.error(f'Error copying table {table} for {date} into database')
                logging.error(traceback.format_exc())
            self.conn.commit()
        logging.info(f'Finished copying {date} into database')
