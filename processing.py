import requests
import pandas as pd
from tqdm import tqdm
import json
import os.path
import subprocess

class Processing:
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
        df = pd.read_csv(self.filename)
        if not ('repo_name' in df.columns and 'sha' in df.columns):
            print('File must have columns repo_name and sha.')
            return
        for index, d in tqdm(df.iterrows(), total=df.shape[0]):
            commit_details = self.fetch_commit_details(d['repo_name'], d['sha'])
            df.at[index, 'commit details'] = commit_details
        df.to_csv(self.filename, index=False)

    def add_user_details(self):
        df = pd.read_csv(self.filename)
        if not ('actor_login' in df.columns):
            print('File must have column actor_login.')
            return
        for index, d in tqdm(df.iterrows(), total=df.shape[0]):
            user_details = self.fetch_user_details(d['actor_login'])
            df.at[index, 'bio'] = user_details.get('bio', '')
            df.at[index, 'location'] = user_details.get('location', '')
            df.at[index, 'blog'] = user_details.get('blog', '')
            df.at[index, 'company'] = user_details.get('company', '')
        df.to_csv(self.filename, index=False)

    def clone_repos(self):
        if not os.path.exists(self.repo_path):
            os.mkdir(self.repo_path)
        if not os.path.isdir(self.repo_path):
            print('Repo path must be a directory.')
            return
        
        df = pd.read_csv(self.filename)
        if not ('repo_name' in df.columns):
            print('File must have column repo_name.')
            return
        for _, d in tqdm(df.iterrows(), total=df.shape[0]):
            self.clone_repo(d['repo_name'])

    def clone_repo(self, repo_name):
        subprocess.run(['git', '-C', self.repo_path, 'clone', f'https://github.com/{repo_name}.git'])

    def fetch_user_details(self, username):
        url = f'https://api.github.com/users/{username}'
        response = requests.get(url, headers=self.headers)
        if response.status_code == 200:
            user_details = response.json()
        elif response.status_code == 403:
            print(response.text)
            exit(1)
        else:
            user_details = {'bio': '', 'location': '', 'blog': '', 'company': ''}
        return user_details
    
    def fetch_commit_details(self, repo, sha):
        url = f'https://api.github.com/repos/{repo}/commits/{sha}'
        response = requests.get(url, headers=self.headers)
        if response.status_code == 200 and 'files' in response.json():
            commit_details = json.dumps(response.json()['files'])
        elif response.status_code == 403:
            print(response.text)
            exit(1)
        else:
            commit_details = f'Commit for not found.'

        return commit_details
