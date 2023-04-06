import requests
import pandas as pd
from tqdm import tqdm
import json
import os.path

class Processing:
    def get_commit_changes(self, filename):
        if not filename.endswith('.csv'):
            print('File must be a csv file.')
            return
        if not os.path.isfile(filename):
            print('File does not exist.')
            return

        df = pd.read_csv(filename)
        if not ('repo_name' in df.columns and 'sha' in df.columns):
            print('File must have columns repo_name and sha.')
            return
        for index, d in tqdm(df.iterrows(), total=df.shape[0]):
            commit_details = self.get_commit_details(d['repo_name'], d['sha'])
            df.at[index, 'commit details'] = commit_details
        df.to_csv(filename, index=False)

    def get_commit_details(self, repo, sha):
        url = f'https://api.github.com/repos/{repo}/commits/{sha}'
        response = requests.get(url)
        if response.status_code == 200 and 'files' in response.json():
            commit_details = json.dumps(response.json()['files'])
        else:
            commit_details = f'Commit for {url} not found.'

        return commit_details


        
        