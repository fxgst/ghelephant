#!/usr/bin/env python3

import logging
import threading
import argparse
from manager import Manager
from database_link import DatabaseLink
from processing import Processing


def main():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--start-date', type=str, required=False, help='Start date in format YYYY-MM-DD')
    parser.add_argument('-e', '--end-date', type=str, required=False, help='End date in format YYYY-MM-DD')
    parser.add_argument('-i', '--create-indices', required=False, help='Create indices for tables', action='store_true')
    parser.add_argument('-t', '--token', type=str, required=False, help='Access token for the GitHub API')
    parser.add_argument('-c', '--add-commit-details', type=str, required=False, help='Append commit details from the GitHub API to a csv file. The csv file must have columns repo_name and sha')
    parser.add_argument('-u', '--add-user-details', type=str, required=False, help='Append user details from the GitHub API to a csv file. The csv file must have the column actor_login')

    args = parser.parse_args()

    if args.create_indices:
        with DatabaseLink() as db:
            db.create_indices()

    elif args.start_date and args.end_date:
        start_year, start_month, start_day = args.start_date.split('-')
        end_year, end_month, end_day = args.end_date.split('-')
        assert int(start_year) >= 2015, 'Start year must be 2015 or later.'

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
    
    elif args.add_commit_details:
        processing = Processing(filename=args.add_commit_details, auth_token=args.token)
        processing.add_commit_details()
    
    elif args.add_user_details:
        processing = Processing(filename=args.add_user_details, auth_token=args.token)
        processing.add_user_details()


if __name__ == '__main__':
    main()
