import psycopg2
import json
from variables import database_name, database_user


class DatabaseLink:
    def __enter__(self):
        self.conn = psycopg2.connect(database=database_name, user=database_user)
        self.cursor = self.conn.cursor()
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.conn.commit()
        self.cursor.close()
        self.conn.close()

    def parse_entry(self, json_data):
        event = json.loads(json_data)

        id = event['id']
        type = event['type']
        actor_id = event['actor']['id']
        actor_login = event['actor']['login']
        repo_id = event['repo']['id']
        repo_name = event['repo']['name']
        payload = json.dumps(event['payload'])
        public = event['public']
        created_at = event['created_at']
        org_id = event['org']['id'] if 'org' in event else None
        org_login = event['org']['login'] if 'org' in event else None

        query = 'INSERT INTO archive ' \
                '(id, type, actor_id, actor_login, repo_id, repo_name, ' \
                'payload, public, created_at, org_id, org_login)' \
                ' VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) ON CONFLICT DO NOTHING'
        data = (id, type, actor_id, actor_login, repo_id, repo_name,
                payload, public, created_at, org_id, org_login)
        self.cursor.execute(query, data)

        # payload = entry['payload']
        # Inserter.insert_actor(self.cursor, entry['actor'])
        # Inserter.insert_repo(self.cursor, entry['repo'])
        # # insert payload

    def create_tables(self):
        self.cursor.execute(open('database/create_tables.sql', 'r').read())
