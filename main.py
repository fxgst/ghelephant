#!/usr/bin/env python3

import logging
import threading
import argparse
from manager import Manager


def main():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--start-date', type=str, required=True, help='Start date in format YYYY-MM-DD')
    parser.add_argument('-e', '--end-date', type=str, required=True, help='End date in format YYYY-MM-DD')
    args = parser.parse_args()
    start_year, start_month, start_day = args.start_date.split('-')
    end_year, end_month, end_day = args.end_date.split('-')

    manager = Manager(start_year=int(start_year), start_month=int(start_month), start_day=int(start_day),
                        end_year=int(end_year), end_month=int(end_month), end_day=int(end_day))
    downloading_thread = threading.Thread(target=manager.run_download, name='downloadingThread')
    downloading_thread.start()
    decompressing_thread = threading.Thread(target=manager.run_decompress, name='decompressingThread')
    decompressing_thread.start()
    writing_thread = threading.Thread(target=manager.run_write_csvs, name='writingThread')
    writing_thread.start()
    copying_thread = threading.Thread(target=manager.run_copy_into_database, name='copyingThread')
    copying_thread.start()


if __name__ == '__main__':
    main()
