import requests
import gzip
import os
import logging
from variables import data_path


class FileManager:
    @staticmethod
    def download_json(date_to_download):
        path = f'{data_path}/{date_to_download}'
        if os.path.isfile(f'{path}.json'):
            return
        # download compressed file
        logging.info(f'Downloading {date_to_download}')
        with open(f'{path}.json.gz', 'wb') as f:
            response = requests.get(f'https://data.gharchive.org/{date_to_download}.json.gz')
            f.write(response.content)
        # decompress file, delete compressed file
        logging.info(f'Decompressing {date_to_download}')
        with gzip.open(f'{path}.json.gz', 'rb') as compressed, open(f'{path}.json', 'wb') as uncompressed:
            uncompressed.write(compressed.read())
        os.remove(f'{path}.json.gz')

    @staticmethod
    def remove_json(date_to_download):
        path = f'{data_path}/{date_to_download}'
        os.remove(f'{path}.json')

    @staticmethod
    def remove_csvs():
        os.system(f'rm {data_path}/*.csv')
