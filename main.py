#!/usr/bin/env python3

import os
import logging

from json_objects import *
from variables import data_path
from file_manager import FileManager
from database_link import DatabaseLink
from inserter import Inserter
from csv_writers import CSVWriters


def copy_insert():
    with DatabaseLink() as db:
        db.create_tables()
        
    with CSVWriters() as writers:
        inserter = Inserter(writers)
        for d in range(21, 27):
            for h in range(0, 24):
                date_to_download = f'2022-11-{str(d).zfill(2)}-{h}'
                FileManager.download_json(date_to_download)
                file_name = f'{data_path}/{date_to_download}.json'
                with open(file_name, 'rb') as f:
                    inserter.write_csvs_events(f)
                    logging.info(f'Finished writing csv for {file_name}')
                # FileManager.remove_json(date_to_download)

    logging.info('Inserting csvs into database...')
    inserter.insert_csvs_into_db()
    
    FileManager.remove_csvs()
        

def preprocess():
    os.system('bash preprocess.sh') # this is too slow
    logging.info('Done preprocessing')


def batch_insert():
    downloader = FileManager(data_path)
    for d in range(23, 24):
        for h in range(0, 24):
            date_to_download = f'2022-11-{str(d).zfill(2)}-{h}'
            downloader.download_json(date_to_download)

    preprocess()
    
    with DatabaseLink() as db:
        db.create_tables()

    for d in range(23, 24):
        for h in range(0, 24):
            date_to_download = f'2022-11-{str(d).zfill(2)}-{h}'
            file_name = f'{data_path}/{date_to_download}.json'

            with open(file_name, 'rb') as f:
                with DatabaseLink() as db:
                    db.batch_insert(f)
                logging.info('Finished inserting file ' + date_to_download + str(h) + '.json')

    logging.info('Inserting csvs into database...')
    Inserter.insert_csvs_into_db()


def generic_insert():
    downloader = FileManager(data_path)
    for d in range(23, 24):
        for h in range(0, 24):
            date_to_download = f'2022-11-{str(d).zfill(2)}-{h}'
            downloader.download_json(date_to_download)

    preprocess()
    
    with DatabaseLink() as db:
        db.create_tables()

    for d in range(23, 24):
        for h in range(0, 24):
            date_to_download = f'2022-11-{str(d).zfill(2)}-{h}'
            file_name = f'{data_path}/{date_to_download}.json'
            with open(file_name, 'r') as f:
                with DatabaseLink() as db:
                    for line in f:
                        db.parse_entry_generic(line)

            
def main():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

    copy_insert()
    # batch_insert()
    # generic_insert()
    

if __name__ == '__main__':
    main()
