from variables import data_path
from file_manager import FileManager
from database_link import DatabaseLink
from json_to_csv_converter import JSONToCSVConverter
from csv_writers import CSVWriters
import logging
import datetime


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
        with CSVWriters() as writers:
            converter = JSONToCSVConverter(writers)
            for date_to_download in self.dates_to_download:
                FileManager.download_json(date_to_download)
                file_name = f'{data_path}/{date_to_download}.json'
                logging.info(f'Writing csv for {date_to_download}')
                with open(file_name, 'rb') as f:
                    converter.write_events(f)
                FileManager.remove_json(date_to_download)

        logging.info('Inserting csvs into database')
        with DatabaseLink() as db:
            db.create_tables()
            db.insert_csvs_into_db()
            db.add_primary_keys()
        FileManager.remove_csvs()

    def __dates_to_download(self) -> list:
        dates_to_download = []
        start_date = datetime.date(self.start_year, self.start_month, self.start_day)
        end_date = datetime.date(self.end_year, self.end_month, self.end_day)
        delta = end_date - start_date
        for i in range(delta.days + 1):
            day = start_date + datetime.timedelta(days=i)
            for h in range(0, 24):
                dates_to_download.append(f'{day.year}-{str(day.month).zfill(2)}-{str(day.day).zfill(2)}-{h}')
        return dates_to_download