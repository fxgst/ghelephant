import requests
import os
import logging
import datetime
from queue import Queue  
from json_to_csv_converter import JSONToCSVConverter
from csv_writers import CSVWriters
from database_link import DatabaseLink


class Manager:
    """
    Class to manage the download, decompression, and writing of data.
    """
    def __init__(self, start_year, start_month, start_day, end_year, end_month, end_day, data_path, sed_name
        database_username, database_password, database_name, database_host, database_port):

        self.start_year = start_year
        self.start_month = start_month
        self.start_day = start_day
        self.end_year = end_year
        self.end_month = end_month
        self.end_day = end_day
        self.dates_to_download = self.__dates_to_download()
        self.downloaded_queue = Queue(maxsize=30)
        self.decompressed_queue = Queue(maxsize=30)
        self.written_queue = Queue(maxsize=2)
        self.data_path = data_path
        self.sed_name = sed_name

        self.DATABASE_USERNAME = database_username
        self.DATABASE_PASSWORD = database_password
        self.DATABASE_NAME = database_name
        self.DATABASE_HOST = database_host
        self.DATABASE_PORT = database_port



    def run_download(self):
        """
        Run the download process. Blocks when queue is empty/full.
        :return: None
        """
        while date := next(self.dates_to_download, None):
            self.download_json(date)
        self.downloaded_queue.put(None)

    def run_decompress(self):
        """
        Run the decompression process. Blocks when queue is empty/full.
        :return: None
        """
        while date := self.downloaded_queue.get():
            self.decompress_json(date)
        self.decompressed_queue.put(None)

    def run_write_csvs(self):
        """
        Run the csv writing process. Blocks when queue is empty/full.
        :return: None
        """
        with DatabaseLink(username=self.DATABASE_USERNAME, self.password=self.DATABASE_PASSWORD, 
            database=self.DATABASE_NAME, host=self.DATABASE_HOST, port=self.DATABASE_PORT, sed_name=self.sed_name) as db:
            db.create_tables()

        converter = JSONToCSVConverter(writer=None)
        while date := self.decompressed_queue.get():
            converter.writer = CSVWriters(date)
            # at the first of the month, reset sets to not use too much memory
            if date[-5:] == '01-23':
                converter.reset_added_sets()
            file_name = f'{self.data_path}/{date}.json'
            logging.info(f'Writing csv for {date}')
            with open(file_name, 'rb') as f:
                converter.write_events(f)
            self.remove_json(date)
            converter.writer.close()
            self.written_queue.put(date)

        self.written_queue.put(None)      

    def run_copy_into_database(self):
        """
        Run the copy into database process. Blocks when queue is empty/full.
        :return: None
        """
        while date := self.written_queue.get():
            logging.info(f'Copying {date} into database')
            with DatabaseLink(username=self.DATABASE_USERNAME, password=self.DATABASE_PASSWORD, 
                database=self.DATABASE_NAME, host=self.DATABASE_HOST, port=self.DATABASE_PORT, sed_name=self.sed_name) as db:
                db.insert_csvs_into_db(date)
            self.remove_inserted_csvs(date)

    def download_json(self, date_to_download):
        """
        Download the json file for the given date.
        :param date_to_download: date to download
        :return: None
        """
        path = f'{self.data_path}/{date_to_download}'
        if os.path.isfile(f'{path}.json'):
            return
        logging.info(f'Downloading {date_to_download}')
        response = requests.get(f'https://data.gharchive.org/{date_to_download}.json.gz')
        if response.status_code != 200:
            logging.error(f'Error downloading {date_to_download}')
            return
        with open(f'{path}.json.gz', 'wb') as f:
            f.write(response.content)
        self.downloaded_queue.put(date_to_download)

    def decompress_json(self, date_to_download):
        """
        Decompress the json file for the given date.
        :param date_to_download: date to decompress
        :return: None
        """
        path = f'{self.data_path}/{date_to_download}'
        if os.path.isfile(f'{path}.json'):
            return
        logging.info(f'Decompressing {date_to_download}')
        os.system(f'gunzip {path}.json.gz')
        self.decompressed_queue.put(date_to_download)

    def __dates_to_download(self):
        """
        Create an iterator of dates to download.
        :return: iterator of dates to download
        """
        dates_to_download = []
        start_date = datetime.date(self.start_year, self.start_month, self.start_day)
        end_date = datetime.date(self.end_year, self.end_month, self.end_day)
        delta = end_date - start_date
        for i in range(delta.days + 1):
            day = start_date + datetime.timedelta(days=i)
            for h in range(0, 24):
                dates_to_download.append(f'{day.year}-{str(day.month).zfill(2)}-{str(day.day).zfill(2)}-{h}')
        dates_to_download.reverse()
        return iter(dates_to_download)

    @staticmethod
    def remove_json(date_to_download):
        """
        Remove the json file for the given date.
        :param date_to_download: date to remove
        :return: None
        """
        path = f'{self.data_path}/{date_to_download}'
        os.remove(f'{path}.json')

    @staticmethod
    def remove_inserted_csvs(day):
        """
        Remove the csv files for the given day.
        :param day: day to remove
        :return: None
        """
        os.system(f'rm {self.data_path}/*-{day}.csv')
