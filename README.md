# GH Elephant

## Installation
* `pip3 install -r requirements.txt`
* complete `variables.py` with your database information and a path where to temporarily store the `json` and `csv` files.
* make sure you have psql running with an empty database as specified in `variables.py`

## Usage

### Creating a Database
* make sure you have about 100 GB of free storage for the temporary files; if that's out of reach, make the queues in `manager.py` smaller.
* run `./ghelephant.py` with the required options `-s` and `-e` specifying start and end date for the downloads in the format "YYYY-MM-DD"
* run `./ghelephant.py` with option `-i` to create indices for faster queries

### Adding Additional Information
If you want to add additional information like user data or get commit details, you can use the GitHub API directly through GH Elephant to enrich your tables.
To do so, you first need to export a table in `csv` format with header (e.g. `copy (select actor_login, repo_name, sha, created_at from archive join commit on payload_id=push_id where type = 'PushEvent' limit 10) to '/my_path/outfile.csv' (format csv, header);`).

Then, you can use the following two commands to extend your table with user data or commit information in JSON form.
You should also use a [Personal GitHub Access Token](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token) and provide it to GH Elepant with the `-t` flag.

* run `./ghelephant.py -u /my_path/outfile.csv` to add user information into the `csv` (requires the presence of the `actor_login` column)
* run `./ghelephant.py -c /my_path/outfile.csv` to add commit information into the `csv` (requires the presence of the `repo_name` and `sha` columns)

### Cloning Repos
If you want to clone some repos you have in your database, export them to a `csv` file with header (see example above).

* run `./ghelephant.py -r /my_path/outfile.csv -o /path/to/folder` (requires the presence of the  `repo_name` column)
