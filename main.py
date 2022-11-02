#!/usr/bin/env python3

from downloader import Downloader
from reader import Reader
from database_link import DatabaseLink
from variables import data_path
import logging

date_to_download = '2022-11-01-'


def main():
    logging.basicConfig(level=logging.INFO)

    # downloader = Downloader(data_path)
    # downloader.download_json(date_to_download)

    with DatabaseLink() as db:
        db.create_tables()

    for h in range(0, 24):
        reader = Reader(data_path)
        json = reader.read_lines(date_to_download + str(h) + '.json')
        with DatabaseLink() as db:
            for entry in json:
                db.parse_entry(entry)
        logging.info('Finished inserting file ' + date_to_download + str(h) + '.json')


if __name__ == '__main__':
    main()
