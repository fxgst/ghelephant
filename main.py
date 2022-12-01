#!/usr/bin/env python3

import logging
from variables import data_path
from file_manager import FileManager
from database_link import DatabaseLink
from json_to_csv_converter import JSONToCSVConverter
from csv_writers import CSVWriters

year = 2022
month = 11
start_day = 10
end_day = 10

def copy_insert():
    with CSVWriters() as writers:
        converter = JSONToCSVConverter(writers)
        for d in range(start_day, end_day + 1):
            for h in range(0, 24):
                date_to_download = f'{year}-{str(month).zfill(2)}-{str(d).zfill(2)}-{h}'
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


def main():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
    copy_insert()


if __name__ == '__main__':
    main()
