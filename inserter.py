import csv
import sys
from json_objects import *
import psycopg2
from variables import *
import orjson
import logging
import os


class Inserter:
    def __init__(self, writers) -> None:
        self.writers = writers
        self.tables = ['archive', 'pushevent', 'commit', 'commitcommentevent', 'releaseevent', 'deleteevent',
            'gollumevent']


    def write_csvs_events(self, f):
        added_ids = set()
        added_pushes = set()

        for line in f:
            generic_event = msgspec.json.decode(line, type=GenericEvent)
            if generic_event.id in added_ids:
                continue
            else:
                added_ids.add(generic_event.id)

            match generic_event.type:
                case 'PushEvent':
                    record = msgspec.json.decode(line, type=PushEvent)
                    if record.payload.push_id in added_pushes:
                        continue
                    else:
                        added_pushes.add(record.payload.push_id)
                    self.insert_pushevent(record, generic_event)
                case 'CommitCommentEvent':
                    self.insert_commitcommentevent(line, generic_event)
                case 'WatchEvent':
                    self.insert_genericevent(generic_event)
                case 'ReleaseEvent':
                    self.insert_releaseevent(line, generic_event)
                case 'DeleteEvent':
                    self.insert_deleteevent(line, generic_event)
                case 'GollumEvent':
                    self.insert_gollumevent(line, generic_event)
                case 'PublicEvent':
                    self.insert_genericevent(generic_event)
                case _:
                    pass


    def insert_gollumevent(self, line: bytes, generic_event: GenericEvent):
        record = msgspec.json.decode(line, type=GollumEvent)
        self.writers.archive.writerow(Inserter.get_archive_record(generic_event, generic_event.id))
        for page in record.payload.pages:
            self.writers.gollumevent.writerow((generic_event.id, page.page_name, page.title, page.summary, page.action, page.sha)) 

    def insert_deleteevent(self, line: bytes, generic_event: GenericEvent):
        record = msgspec.json.decode(line, type=DeleteEvent)
        self.writers.archive.writerow(Inserter.get_archive_record(generic_event, int(generic_event.id)))
        self.writers.deleteevent.writerow((generic_event.id, record.payload.ref[:255], record.payload.ref_type,
            record.payload.pusher_type))

    def insert_releaseevent(self, line: bytes, generic_event: GenericEvent):
        record = msgspec.json.decode(line, type=ReleaseEvent)
        release = record.payload.release
        self.writers.archive.writerow(Inserter.get_archive_record(generic_event, release.id))
        self.writers.releaseevent.writerow((release.id, release.node_id, release.tag_name,
            release.target_commitish, release.name, release.draft, release.prerelease,
            release.created_at, release.published_at, release.body))
    

    def insert_pushevent(self, record: PushEvent, generic_event: GenericEvent):
        self.writers.archive.writerow(Inserter.get_archive_record(generic_event, record.payload.push_id))
        self.writers.pushevent.writerow((record.payload.push_id, record.payload.size, 
            record.payload.distinct_size, record.payload.ref[:255], record.payload.head,
            record.payload.before))
        for commit in record.payload.commits:
            self.writers.commit.writerow((commit.sha, record.payload.push_id,
                commit.author.email[:255], commit.author.name[:255], commit.message, commit.distinct))
                

    def insert_commitcommentevent(self, line: bytes, generic_event: GenericEvent):
        record = orjson.loads(line)
        c = record['payload']['comment']
        self.writers.archive.writerow(Inserter.get_archive_record(generic_event, c['id']))
        self.writers.commitcommentevent.writerow((c['id'], c['node_id'], c['position'], c['line'],
            c['path'], c['commit_id'], c['author_association'], c['body'],
            c['reactions']['total_count'], c['reactions']['+1'], c['reactions']['-1'],
            c['reactions']['laugh'], c['reactions']['hooray'], c['reactions']['confused'],
            c['reactions']['heart'], c['reactions']['rocket'], c['reactions']['eyes']))


    def insert_genericevent(self, generic_event: GenericEvent):
        self.writers.archive.writerow(Inserter.get_archive_record(generic_event))


    def insert_csvs_into_db(self):
        # conn = psycopg.connect(f'dbname={database_name} user={database_user}')
        with psycopg2.connect(database=database_name, user=database_user) as conn:
            with conn.cursor() as cursor:
                for table in self.tables:
                    query = f"COPY {table} FROM '{data_path}/{table}.csv' WITH (FORMAT csv)"
                    try:
                        cursor.execute(query)
                    except psycopg2.errors.CharacterNotInRepertoire:
                        logging.error(f'Error in table {table}, removing null bytes')
                        conn.rollback()
                        os.system(f"{sed_name} -i 's/\\x00//g' {data_path}/{table}.csv")
                        cursor.execute(query)
                    conn.commit()
                    logging.info(f'Inserted {table} into database')  


    @staticmethod
    def write_csvs_push_event_orjson(data):
        file_name = f'{data_path}/my'
        with open(file_name+'.csv', 'a') as archive, open(file_name+'_commits.csv', 'a') as commits, open(file_name+'_pushes.csv', 'a') as pushes:
            writer_a = csv.writer(archive)
            writer_c = csv.writer(commits)
            writer_p = csv.writer(pushes)

            for l in data:
                # record = msgspec.json.decode(l, type=PushEvent)
                event = orjson.loads(l)
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
                push_id = event['payload']['push_id']
                a = (id, type, actor_id, actor_login, repo_id, repo_name,
                        push_id, public, created_at, org_id, org_login)
                writer_a.writerow(a)

                event = event['payload']
                size = event['size']
                distinct_size = event['distinct_size']
                ref = event['ref']
                head = event['head']
                before = event['before']

                p = (push_id, size, distinct_size, ref, head, before)
                writer_p.writerow(p)
                for commit in event['commits']:

                    sha = commit['sha']
                    author_email = commit['author']['email']
                    author_name = commit['author']['name']
                    message = commit['message']
                    distinct = commit['distinct']

                    c = (sha, push_id, author_email, author_name, message, distinct)
                    writer_c.writerow(c)   


    @staticmethod
    def get_archive_record(record: GenericEvent, payload_id = None) -> tuple:
        org_id = record.org.id if record.org else None
        org_login = record.org.login if record.org else None

        return (record.id, record.type, record.actor.id, record.actor.login, record.repo.id, 
                record.repo.name, payload_id, record.public, record.created_at,
                org_id, org_login)


    @staticmethod
    def write_csvs_push_event(data, file_name):
        file_name = f'{data_path}/my'
        added_ids = set()
        added_pushes = set()

        with open(file_name+'.csv', 'a') as archive, open(file_name+'_commits.csv', 'a') as commits, open(file_name+'_pushes.csv', 'a') as pushes:
            writer_a = csv.writer(archive)
            writer_c = csv.writer(commits)
            writer_p = csv.writer(pushes)

            for l in data:
                generic_event = msgspec.json.decode(l, type=GenericEvent)
                if generic_event.id in added_ids:
                    continue
                else:
                    added_ids.add(generic_event.id)

                record = msgspec.json.decode(l, type=PushEvent)
                writer_a.writerow(Inserter.get_archive_record(generic_event, record.payload.push_id))

                if record.payload.push_id in added_pushes:
                    continue
                else:
                    added_pushes.add(record.payload.push_id)
                writer_p.writerow((record.payload.push_id, record.payload.size, record.payload.distinct_size, record.payload.ref[:255], record.payload.head, record.payload.before))

                for commit in record.payload.commits:
                    writer_c.writerow((commit.sha, record.payload.push_id, commit.author.email[:255], commit.author.name[:255], commit.message, commit.distinct))
    

    # @staticmethod
    # def insert_actor(cursor, actor):
    #     query = 'INSERT INTO actor (id, login) VALUES (%s, %s) ON CONFLICT DO NOTHING'
    #     data = (actor['id'], actor['login'])
    #     cursor.execute(query, data)

    # @staticmethod
    # def insert_repo(cursor, repo):
    #     owner, name = repo['name'].split('/')

    #     data = (repo['id'], owner, name)
    #     query = 'INSERT INTO repo (id, owner, name) VALUES (%s, %s, %s) ON CONFLICT DO NOTHING'
    #     cursor.execute(query, data)

    # @staticmethod
    # def insert_push_event(cursor, payload):
    #     push_id = payload['push_id']
    #     size = payload['size']
    #     distinct_size = payload['distinct_size']
    #     ref = payload['ref']
    #     head = payload['head']
    #     before = payload['before']

    #     query = 'INSERT INTO pushevent (push_id, size, distinct_size, ref, head, before) '
    #     query += 'VALUES (%s, %s, %s, %s, %s, %s) ON CONFLICT DO NOTHING'
    #     data = (push_id, size, distinct_size, ref, head, before)
    #     cursor.execute(query, data)

    #     for commit in payload['commits']:
    #         sha = commit['sha']
    #         author_email = commit['author']['email']
    #         author_name = commit['author']['name']
    #         message = commit['message']
    #         distinct = commit['distinct']

    #         query = 'INSERT INTO commit (sha, push_id, author_email, author_name, message, is_distinct) '
    #         query += 'VALUES (%s, %s, %s, %s, %s, %s) ON CONFLICT DO NOTHING'
    #         data = (sha, push_id, author_email, author_name, message, distinct)
    #         cursor.execute(query, data)

    # @staticmethod
    # def insert_push_event_msgspec(cursor, payload):
    #     query = 'INSERT INTO pushevent (push_id, size, distinct_size, ref, head, before) '
    #     query += 'VALUES (%s, %s, %s, %s, %s, %s) ON CONFLICT DO NOTHING'
    #     data = (payload.push_id, payload.size, payload.distinct_size, payload.ref, payload.head, payload.before)
    #     cursor.execute(query, data)

    #     for commit in payload.commits:
    #         query = 'INSERT INTO commit (sha, push_id, author_email, author_name, message, is_distinct) '
    #         query += 'VALUES (%s, %s, %s, %s, %s, %s) ON CONFLICT DO NOTHING'
    #         data = (commit.sha, payload.push_id, commit.author.email, commit.author.name, commit.message, commit.distinct)
    #         cursor.execute(query, data)