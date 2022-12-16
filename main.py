#!/usr/bin/env python3

import logging
from scheduler import Scheduler


def main():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
    scheduler = Scheduler(start_year=2022, start_month=1, start_day=1, end_year=2022, end_month=12, end_day=15)
    scheduler.fast_insert()


if __name__ == '__main__':
    main()
