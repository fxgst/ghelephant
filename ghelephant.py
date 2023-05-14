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
    parser.add_argument('-s', '--start-date', type=str, required=False, help='Start date in format YYYY-MM-DD.')
    parser.add_argument('-e', '--end-date', type=str, required=False, help='End date in format YYYY-MM-DD.')
    parser.add_argument('-i', '--create-indices', required=False, help='Create indices for tables.',
                        action='store_true')
    parser.add_argument('-t', '--token', type=str, required=False, help='Access token for the GitHub API.')
    parser.add_argument('-c', '--add-commit-details', type=str, required=False,
                        help='Append commit details from the GitHub API to a csv file. '
                             'The csv file must have columns "repo_name" and "sha".')
    parser.add_argument('-u', '--add-user-details', type=str, required=False,
                        help='Append user details from the GitHub API to a csv file. '
                             'The csv file must have the column "actor_login".')
    parser.add_argument('-r', '--clone-repos', type=str, required=False,
                        help='Clone repos listed in a csv file from GitHub into a folder.'
                             'Use in conjunction with -o and specify an empty folder where to clone the repos to.'
                             'The csv file must have the column "repo_name".')
    parser.add_argument('-o', '--outpath', type=str, required=False,
                        help='The path where to clone the repos to. Only use in conjunction with -r.')
    parser.add_argument('-l', '--add-country-details', type=str, required=False,
                        help='Append country details for users from the GitHub API to a csv file. '
                             'The csv file must have the column "location". '
                             'This option should be used only after running with option `-u` which added the column '
                             '"location" to the csv file.')
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

    elif args.clone_repos and args.outpath:
        processing = Processing(filename=args.clone_repos, repo_path=args.outpath)
        processing.clone_repos()

    elif args.add_country_details:
        processing = Processing(filename=args.add_country_details)
        processing.add_country_details()

    else:
        parser.print_help()


if __name__ == '__main__':
    main()
