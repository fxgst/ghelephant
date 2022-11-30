import psycopg2
import json
import orjson
from variables import database_name, database_user
from inserter import Inserter
import csv
import msgspec
from json_objects import *

class DatabaseLink:
    def __enter__(self):
        self.conn = psycopg2.connect(database=database_name, user=database_user)
        # self.conn = psycopg.connect(f'dbname={database_name} user={database_user}')
        self.cursor = self.conn.cursor()
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.conn.commit()
        self.cursor.close()
        self.conn.close()

    def insert_push_event_msgspec_multiple(self, records):
        args_str = b','.join(self.cursor.mogrify('(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)', r) for r in records)
        self.cursor.execute('INSERT INTO archive ' \
                '(id, type, actor_id, actor_login, repo_id, repo_name, ' \
                'push_id, public, created_at, org_id, org_login) VALUES ' + args_str.decode())

    def insert_push_msgspec_multiple(self, records):
        args_str = b','.join(self.cursor.mogrify('(%s,%s,%s,%s,%s,%s)', r) for r in records)
        self.cursor.execute('INSERT INTO pushevent ' \
                '(push_id, size, distinct_size, ref, head, before) VALUES ' + args_str.decode())

    def insert_commit_msgspec_multiple(self, records):
        args_str = b','.join(self.cursor.mogrify('(%s,%s,%s,%s,%s,%s)', r) for r in records)
        self.cursor.execute('INSERT INTO commit ' \
                '(sha, push_id, author_email, author_name, message, is_distinct) VALUES ' + args_str.decode())
    
    def batch_insert(self, f):
        records = []
        pushes = []
        commits = []
        for line in f:
            record = msgspec.json.decode(line, type=PushEvent)
            org_id = record.org.id if record.org else None
            org_login = record.org.login if record.org else None
            r = (record.id, record.type, record.actor.id, record.actor.login, record.repo.id, 
                    record.repo.name, record.payload.push_id, record.public, record.created_at,
                    org_id, org_login)
            p = (record.payload.push_id, record.payload.size, record.payload.distinct_size, record.payload.ref, record.payload.head, record.payload.before)
            records.append(r)
            pushes.append(p)
            for commit in record.payload.commits:
                commits.append((commit.sha, record.payload.push_id, commit.author.email, commit.author.name, commit.message, commit.distinct))

            if len(records) % 1250 == 0:
                self.insert_push_event_msgspec_multiple(records)
                self.insert_push_msgspec_multiple(pushes)
                self.insert_commit_msgspec_multiple(commits)
                records = []
                pushes = []
                commits = []

        # insert the rest
        self.insert_push_event_msgspec_multiple(records)
        self.insert_push_msgspec_multiple(pushes)
        self.insert_commit_msgspec_multiple(commits)


    # def insert_push_event_msgspec(self, record):
    #     actor = record.actor
    #     repo = record.repo
    #     payload = record.payload
    #     org_id = record.org.id if record.org else None
    #     org_login = record.org.login if record.org else None

    #     query = 'INSERT INTO archive ' \
    #             '(id, type, actor_id, actor_login, repo_id, repo_name, ' \
    #             'push_id, public, created_at, org_id, org_login)' \
    #             ' VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) ON CONFLICT DO NOTHING'
    #     data = (record.id, record.type, actor.id, actor.login, repo.id, repo.name,
    #             payload.push_id, record.public, record.created_at, org_id, org_login)
    #     self.cursor.execute(query, data)
    #     Inserter.insert_push_event_msgspec(self.cursor, payload)


    # def getrecord_orjson(self, event) -> tuple:
    #     id = event['id']
    #     type = event['type']
    #     actor_id = event['actor']['id']
    #     actor_login = event['actor']['login']
    #     repo_id = event['repo']['id']
    #     repo_name = event['repo']['name']
    #     public = event['public']
    #     created_at = event['created_at']
    #     org_id = event['org']['id'] if 'org' in event else None
    #     org_login = event['org']['login'] if 'org' in event else None
    #     push_id = event['payload']['push_id']
    #     return (id, type, actor_id, actor_login, repo_id, repo_name,
    #             push_id, public, created_at, org_id, org_login)

    # def parse_push_event(self, event):
    #     event = orjson.loads(event)

    #     id = event['id']
    #     type = event['type']
    #     actor_id = event['actor']['id']
    #     actor_login = event['actor']['login']
    #     repo_id = event['repo']['id']
    #     repo_name = event['repo']['name']
    #     public = event['public']
    #     created_at = event['created_at']
    #     org_id = event['org']['id'] if 'org' in event else None
    #     org_login = event['org']['login'] if 'org' in event else None

    #     push_id = event['payload']['push_id']

    #     query = 'INSERT INTO archive ' \
    #             '(id, type, actor_id, actor_login, repo_id, repo_name, ' \
    #             'push_id, public, created_at, org_id, org_login)' \
    #             ' VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) ON CONFLICT DO NOTHING'
    #     data = (id, type, actor_id, actor_login, repo_id, repo_name,
    #             push_id, public, created_at, org_id, org_login)
    #     self.cursor.execute(query, data)
    #     Inserter.insert_push_event(self.cursor, event['payload'])


    def parse_entry_generic(self, json_data):
        event = json.loads(json_data)

        id = event['id']
        type = event['type']
        actor_id = event['actor']['id']
        actor_login = event['actor']['login']
        repo_id = event['repo']['id']
        repo_name = event['repo']['name']
        public = event['public']
        created_at = event['created_at']
        org_id = event['org']['id'] if 'org' in event else None
        org_login = event['org']['login'] if 'org' in event else None

        payload = json.dumps(event['payload'])
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
        self.cursor.execute(open('sql/create_tables.sql', 'r').read())
