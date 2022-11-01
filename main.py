#!/usr/bin/env python3

from downloader import Downloader
from parser import Parser
from database_link import DatabaseLink
from variables import data_path
import logging

date_to_download = '2022-10-15-1'

def main():
    logging.basicConfig(level=logging.INFO)

    downloader = Downloader(data_path)
    downloader.download_json(date_to_download)
    parser = Parser(data_path)
    json = parser.read_lines(date_to_download + '.json')
    
    with DatabaseLink() as db:
        db.insert_json(json)

    
if __name__ == '__main__':
    main()
