# ghelephant

## installation
* `pip3 install requests psycopg2 orjson msgspec`
* complete `variables.py` with your database information and a path where to temporarily store the `.json` and `.csv` files.
* make sure you have psql running with an empty database as specified in `variables.py`

## usage
* run `./main.py` with the required options `-s` and `-e` specifying start and end date for the downloads in the format "YYYY-MM-DD"
