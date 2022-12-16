import requests
import gzip
import os
import logging
from variables import data_path
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
import threading


class FSWatcher(FileSystemEventHandler):
    def __init__(self, dates_to_download, threshold) -> None:
        super().__init__()
        self.dates_to_download = dates_to_download
        self.threshold = threshold

    def on_deleted(self, event):
        # after a file is deleted, download next files
        while len([f for f in os.listdir(data_path) if f.endswith('.json')]) < self.threshold:
            file = next(self.dates_to_download, None)
            if not file:
                return
            DownloadManager.download_json(file)
            # decompress json in separate thread
            decompress_thread = threading.Thread(target=DownloadManager.decompress_json, args=(file, True))
            decompress_thread.start()      


class DownloadManager:
    @staticmethod
    def run(dates_to_download, threshold):
        observer = Observer()
        observer.schedule(FSWatcher(dates_to_download, threshold), data_path)
        observer.start()

    @staticmethod
    def download_and_decompress_json(date_to_download):
        DownloadManager.download_json(date_to_download)
        DownloadManager.decompress_json(date_to_download)

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
    
    @staticmethod
    def decompress_json(date_to_download, should_exit=False):
        path = f'{data_path}/{date_to_download}'
        if os.path.isfile(f'{path}.json'):
            return
        # decompress file, delete compressed file
        logging.info(f'Decompressing {date_to_download}')
        with gzip.open(f'{path}.json.gz', 'rb') as compressed, open(f'{path}.json.inprogress', 'wb') as uncompressed:
            uncompressed.write(compressed.read())
        os.rename(f'{path}.json.inprogress', f'{path}.json')
        os.remove(f'{path}.json.gz')
        if should_exit:
            exit()

    @staticmethod
    def remove_json(date_to_download):
        path = f'{data_path}/{date_to_download}'
        os.remove(f'{path}.json')

    @staticmethod
    def remove_csvs():
        os.system(f'rm {data_path}/*.csv')

    @staticmethod
    def remove_insert_csvs():
        os.system(f'rm {data_path}/*.csv.insert')
