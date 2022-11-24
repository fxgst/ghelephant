#!/usr/bin/env python3

import os
import logging

from variables import data_path
from json_objects import *
from downloader import Downloader
from database_link import DatabaseLink
from inserter import Inserter



def main():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

    downloader = Downloader(data_path)
    for d in range(9, 16):
        for h in range(0, 24):
            date_to_download = f'2022-11-{str(d).zfill(2)}-{h}'
            downloader.download_json(date_to_download)

    # run preprocessing script
    # os.system('bash preprocess.sh')
    
    with DatabaseLink() as db:
        db.create_tables()

    for d in range(9, 16):
        for h in range(0, 24):
            file_name = f'{data_path}/2022-11-{str(d).zfill(2)}-{h}.json'
            with open(file_name, 'rb') as f:
                # BATCH INSERT
                # with DatabaseLink() as db:
                #     db.batch_insert(f)
                # logging.info('Finished inserting file ' + date_to_download + str(h) + '.json')

                # COPY INSERT
                Inserter.write_csvs_push_event(f, file_name)
                logging.info(f'Finished writing csv for {file_name}')
    logging.info('Inserting csvs into database...')
    Inserter.insert_csvs_into_db()


if __name__ == '__main__':
    main()
