import requests
import gzip
import os
import logging

class Downloader:
    def __init__(self, data_path):
        self.data_path = data_path

    def download_json(self, date_to_download):
        path = f'{self.data_path}/{date_to_download}'

        if os.path.isfile(f'{path}.json'):
            return
        logging.info(f'Downloading {date_to_download} ...')   
        # download compressed file
        with open(f'{path}.json.gz', 'wb') as f:
            response = requests.get(f'https://data.gharchive.org/{date_to_download}.json.gz')
            f.write(response.content)
        # decompress file, delete compressed file
        with gzip.open(f'{path}.json.gz', 'rb') as compressed, open(f'{path}.json', 'wb') as uncompressed:
            uncompressed.write(compressed.read())
            os.remove(f'{path}.json.gz')
        logging.info('Done')
