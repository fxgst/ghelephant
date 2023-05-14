import csv
from variables import data_path


class CSVWriters:
    """
    Class to manage different CSV writers.
    """
    file_names = ['archive', 'commit', 'pushevent', 'commitcommentevent', 'releaseevent', 'deleteevent',
            'gollumevent', 'memberevent', 'forkevent', 'createevent', 'issue', 'issuecomment', 'pullrequest',
            'pullrequestreview', 'pullrequestreviewcomment']

    def __init__(self, date):
        """
        Create a CSV writer for each table/file
        :param date: date of the data to be written
        """
        self.files = [open(f'{data_path}/{file_name}-{date}.csv', 'a') for file_name in CSVWriters.file_names]
        self.writers = {name : csv.writer(f, escapechar='🁇') for f, name in zip(self.files, CSVWriters.file_names)}

    def close(self):
        """
        Close all writers
        :return: None
        """
        for file in self.files:
            file.close()
