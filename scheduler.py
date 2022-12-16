from variables import data_path
from download_manager import DownloadManager
from database_link import DatabaseLink
from json_to_csv_converter import JSONToCSVConverter
from csv_writers import CSVWriters
import logging
import datetime
import threading
import time
import os

class Scheduler:
    def __init__(self, start_year, start_month, start_day, end_year, end_month, end_day):
        self.start_year = start_year
        self.start_month = start_month
        self.start_day = start_day
        self.end_year = end_year
        self.end_month = end_month
        self.end_day = end_day
        self.dates_to_download = self.__dates_to_download()

    def copy_insert(self):
        files_iterator = iter(self.dates_to_download)
        DownloadManager.download_and_decompress_json(next(files_iterator))
        download_thread = threading.Thread(target=DownloadManager.run, args=(files_iterator, 10))
        download_thread.start()

        writers = CSVWriters()
        converter = JSONToCSVConverter(writers, set(), set(), set(), set())

        with DatabaseLink() as db:
            db.create_tables()

        for hour, date_to_download in enumerate(self.dates_to_download):
            file_name = f'{data_path}/{date_to_download}.json'
            # wait for file to be ready
            while not os.path.isfile(file_name):
                time.sleep(0.05)
            self.__write_and_insert(hour, date_to_download, converter)

        download_thread.join()
        with DatabaseLink() as db:
            db.add_primary_keys()

    def copy_insert_sequential(self):
        writers = CSVWriters()
        converter = JSONToCSVConverter(writers, set(), set(), set(), set())

        with DatabaseLink() as db:
            db.create_tables()
        for hour, date_to_download in enumerate(self.dates_to_download):
            DownloadManager.download_and_decompress_json(date_to_download)
            self.__write_and_insert(hour, date_to_download, converter)
        with DatabaseLink() as db:
            db.add_primary_keys()

    def __write_and_insert(self, hour, date_to_download, converter):
        file_name = f'{data_path}/{date_to_download}.json'
        logging.info(f'Writing csv for {date_to_download}')
        with open(file_name, 'rb') as f:
            converter.write_events(f)
            DownloadManager.remove_json(date_to_download)

        if hour % 24 == 24 - 1:
            converter.writers.close()
            logging.info('Inserting csvs into database')
            with DatabaseLink() as db:
                db.insert_csvs_into_db()
            DownloadManager.remove_csvs()
            converter.writers = CSVWriters()

    def __dates_to_download(self) -> list:
        dates_to_download = []
        start_date = datetime.date(self.start_year, self.start_month, self.start_day)
        end_date = datetime.date(self.end_year, self.end_month, self.end_day)
        delta = end_date - start_date
        for i in range(delta.days + 1):
            day = start_date + datetime.timedelta(days=i)
            for h in range(0, 24):
                dates_to_download.append(f'{day.year}-{str(day.month).zfill(2)}-{str(day.day).zfill(2)}-{h}')
        dates_to_download.reverse()
        return dates_to_download
