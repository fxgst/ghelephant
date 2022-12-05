from variables import data_path
import csv


class CSVWriters:
    def __init__(self):
        escapechar = '\\'
        mode = 'a'
        self.archive_f = open(f'{data_path}/archive.csv', mode)
        self.commit_f = open(f'{data_path}/commit.csv', mode)
        self.pushevent_f = open(f'{data_path}/pushevent.csv', mode)
        self.commitcommentevent_f = open(f'{data_path}/commitcommentevent.csv', mode)
        self.releaseevent_f = open(f'{data_path}/releaseevent.csv', mode)
        self.deleteevent_f = open(f'{data_path}/deleteevent.csv', mode)
        self.gollumevent_f = open(f'{data_path}/gollumevent.csv', mode)
        self.memberevent_f = open(f'{data_path}/memberevent.csv', mode)
        self.forkevent_f = open(f'{data_path}/forkevent.csv', mode)
        self.createevent_f = open(f'{data_path}/createevent.csv', mode)
        self.issuesevent_f = open(f'{data_path}/issuesevent.csv', mode)

        self.archive = csv.writer(self.archive_f, escapechar=escapechar)
        self.commit = csv.writer(self.commit_f, escapechar=escapechar)
        self.pushevent = csv.writer(self.pushevent_f, escapechar=escapechar)
        self.commitcommentevent = csv.writer(self.commitcommentevent_f, escapechar=escapechar)
        self.releaseevent = csv.writer(self.releaseevent_f, escapechar=escapechar)
        self.deleteevent = csv.writer(self.deleteevent_f, escapechar=escapechar)
        self.gollumevent = csv.writer(self.gollumevent_f, escapechar=escapechar)
        self.memberevent = csv.writer(self.memberevent_f, escapechar=escapechar)
        self.forkevent = csv.writer(self.forkevent_f, escapechar=escapechar)
        self.createevent = csv.writer(self.createevent_f, escapechar=escapechar)
        self.issuesevent = csv.writer(self.issuesevent_f, escapechar=escapechar)

    def __enter__(self):
        self.__init__()
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.close()

    def close(self):
        self.archive_f.close()
        self.commit_f.close()
        self.pushevent_f.close()
        self.commitcommentevent_f.close()
        self.releaseevent_f.close()
        self.deleteevent_f.close()
        self.gollumevent_f.close()
        self.memberevent_f.close()
        self.forkevent_f.close()
        self.createevent_f.close()
        self.issuesevent_f.close()
