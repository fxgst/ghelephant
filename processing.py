import requests
import json
import os.path
import subprocess
import time
import pycountry
import pandas as pd
from tqdm import tqdm
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut

class Processing:
    """
    Additional commands for GH Elephant: process csv data and enrich it with additional data.
    """
    def __init__(self, filename, auth_token=None, repo_path=None):
        self.headers = {'Authorization': 'Token ' + auth_token} if auth_token else None
        self.repo_path = repo_path if repo_path else '.'
        if not filename.endswith('.csv'):
            print('File must be a csv file.')
            return
        if not os.path.isfile(filename):
            print('File does not exist.')
            return
        self.filename = filename

    def add_commit_details(self):
        """
        Add commit details to a csv file.
        :return: None
        """
        df = pd.read_csv(self.filename)
        seen = dict()
        if not ('repo_name' in df.columns and 'sha' in df.columns):
            print('File must have columns "repo_name" and "sha".')
            return
        for index, d in tqdm(df.iterrows(), total=df.shape[0]):
            repo = d['repo_name']
            sha = d['sha']
            if (repo, sha) not in seen:
                print('Fetching commit details for', repo, sha)
                seen[(repo, sha)] = self.fetch_commit_details(repo, sha)
            df.at[index, 'commit details'] = seen[(repo, sha)]
        df.to_csv(self.filename, index=False)

    def add_user_details(self):
        """
        Add user details to a csv file.
        :return: None
        """
        df = pd.read_csv(self.filename)
        seen = dict()
        if not ('actor_login' in df.columns):
            print('File must have column "actor_login".')
            return
        for index, d in tqdm(df.iterrows(), total=df.shape[0]):
            actor = d['actor_login']
            if actor not in seen:
                seen[actor] = self.fetch_user_details(actor)
            df.at[index, 'bio'] = seen[actor].get('bio', '')
            df.at[index, 'location'] = seen[actor].get('location', '')
            df.at[index, 'blog'] = seen[actor].get('blog', '')
            df.at[index, 'company'] = seen[actor].get('company', '')      

        df.to_csv(self.filename, index=False)

    def clone_repos(self):
        """
        Clone repos appearing in csv file.
        :return: None
        """
        if not os.path.exists(self.repo_path):
            os.mkdir(self.repo_path)
        if not os.path.isdir(self.repo_path):
            print('Repo path must be a directory.')
            return
        
        df = pd.read_csv(self.filename)
        if not ('repo_name' in df.columns):
            print('File must have column "repo_name".')
            return
        seen = set()
        for _, d in tqdm(df.iterrows(), total=df.shape[0]):
            if d['repo_name'] not in seen:
                seen.add(d['repo_name'])
                self.clone_repo(d['repo_name'])

    def clone_repo(self, repo_name):
        """
        Clone a singe repo.
        :param repo_name: name of the repo to clone.
        :return: None
        """
        subprocess.run(['git', '-C', self.repo_path, 'clone', f'https://github.com/{repo_name}.git'])

    def fetch_user_details(self, username):
        """
        Fetch user details like bio, location, blog, company from GitHub API.
        :param username: username of the user to fetch details for.
        :return: user details
        """
        url = f'https://api.github.com/users/{username}'
        response = requests.get(url, headers=self.headers)
        if response.status_code == 200:
            user_details = response.json()
        elif response.status_code == 403:
            if int(response.headers['X-RateLimit-Remaining']) == 0:
                # sleep until reset
                target_timestamp = int(response.headers['X-RateLimit-Reset'])
                current_timestamp = int(time.time())  # get the current Unix timestamp
                seconds_to_sleep = target_timestamp - current_timestamp  # calculate the time difference
                print(f'Rate limit of {response.headers["X-RateLimit-Limit"]} reached, sleeping until {target_timestamp + 1}')
                if seconds_to_sleep > 0:
                    time.sleep(seconds_to_sleep + 1)
                return self.fetch_user_details(username)
            else:
                print(response.text)
                exit(1)
        else:
            user_details = {'bio': '', 'location': '', 'blog': '', 'company': ''}
        return user_details
    
    def fetch_commit_details(self, repo, sha):
        """
        Fetch commit details from GitHub API in JSON format.
        :param repo: the repo name in the format "owner/repo"
        :param sha: the commit sha
        :return: commit details in JSON format
        """
        url = f'https://api.github.com/repos/{repo}/commits/{sha}'
        response = requests.get(url, headers=self.headers)
        if response.status_code == 200 and 'files' in response.json():
            commit_details = json.dumps(response.json()['files'])
        elif response.status_code == 403:
            if int(response.headers['X-RateLimit-Remaining']) == 0:
                # sleep until reset
                target_timestamp = int(response.headers['X-RateLimit-Reset'])
                current_timestamp = int(time.time())  # get the current Unix timestamp
                seconds_to_sleep = target_timestamp - current_timestamp  # calculate the time difference
                print(f'Rate limit of {response.headers["X-RateLimit-Limit"]} reached, sleeping until {target_timestamp + 1}')
                if seconds_to_sleep > 0:
                    time.sleep(seconds_to_sleep + 1)
                return self.fetch_commit_details(repo, sha)
            else:
                print(response.text)
                exit(1)
        else:
            commit_details = f'Commit for not found.'

        return commit_details
    
    def add_country_details(self):
        """
        Add country details to a csv file. This function uses the Nominatim API to get the country alpha_2 code from
        the location string.
        :return: None
        """
        df = pd.read_csv(self.filename)
        if not ('location' in df.columns):
            print('File must have column "location". Run with option --add-user-details first.')
            return

        geolocator = Nominatim(user_agent="ghelephant")

        # Function to get the country alpha_2 code from a location string
        def get_country_alpha2(location):
            try:
                geocode_result = geolocator.geocode(location, timeout=10)
                if geocode_result:
                    reverse_result = geolocator.reverse((geocode_result.latitude, geocode_result.longitude), timeout=10)
                    if reverse_result:
                        address = reverse_result.raw['address']
                        if 'country_code' in address:
                            return address['country_code'].upper()
                    else:
                        print('No reverse result for location: {}'.format(location))
            except GeocoderTimedOut:
                return None

        # Function to convert alpha_2 to alpha_3 country codes
        def alpha2_to_alpha3(alpha_2_code):
            try:
                return pycountry.countries.get(alpha_2=alpha_2_code).alpha_3
            except AttributeError:
                return None

        df['country_code_alpha3'] = None
        df['country_code_alpha2'] = None
        cache_alpha2 = {}
        cache_alpha3 = {}
        for index, row in tqdm(df.iterrows(), total=df.shape[0]):
            if pd.notna(row['location']):
                location = row['location']
                if location not in cache_alpha2:
                    cache_alpha2[location] = get_country_alpha2(location)
                alpha2_code = cache_alpha2[location]

                df.at[index, 'country_code_alpha2'] = alpha2_code
                if alpha2_code:
                    if alpha2_code not in cache_alpha3:
                        cache_alpha3[alpha2_code] = alpha2_to_alpha3(alpha2_code)
                    alpha3_code = cache_alpha3[alpha2_code]
                    df.at[index, 'country_code_alpha3'] = alpha3_code

        df.to_csv(self.filename, index=False)

