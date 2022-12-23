import csv
from variables import data_path


class CSVWriters:
    file_names = ['archive', 'commit', 'pushevent', 'commitcommentevent', 'releaseevent', 'deleteevent',
            'gollumevent', 'memberevent', 'forkevent', 'createevent', 'issue', 'issuecomment', 'pullrequest',
            'pullrequestreview', 'pullrequestreviewcomment']

    def __init__(self, date):
        self.files = [open(f'{data_path}/{file_name}-{date}.csv', 'a') for file_name in CSVWriters.file_names]
        self.writers = {name : csv.writer(f, escapechar='°') for f, name in zip(self.files, CSVWriters.file_names)}

    def close(self):
        for file in self.files:
            file.close()
