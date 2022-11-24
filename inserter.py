import csv
import sys
from json_objects import *
import psycopg2
from variables import *
import orjson
import logging

class Inserter:
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
                record = msgspec.json.decode(l, type=PushEvent)
                if record.id in added_ids:
                    print('Duplicate id found' + str(datetime.timestamp))
                    continue
                else:
                    added_ids.add(record.id)
                writer_a.writerow(Inserter.getrecord(record))

                if record.payload.push_id in added_pushes:
                    continue
                else:
                    added_pushes.add(record.payload.push_id)
                writer_p.writerow((record.payload.push_id, record.payload.size, record.payload.distinct_size, record.payload.ref[:255], record.payload.head, record.payload.before))

                for commit in record.payload.commits:
                    writer_c.writerow((commit.sha, record.payload.push_id, commit.author.email[:255], commit.author.name[:255], commit.message, commit.distinct))
        
    
    @staticmethod
    def insert_csvs_into_db():
        conn = psycopg2.connect(database=database_name, user=database_user)
        # conn = psycopg.connect(f'dbname={database_name} user={database_user}')
        cursor = conn.cursor()

        file_name = f'{data_path}/my'
        query = f"COPY archive FROM '{file_name}.csv' WITH (FORMAT csv)"
        cursor.execute(query)
        logging.info("Inserted archive")
        query = f"COPY pushevent FROM '{file_name}_pushes.csv' WITH (FORMAT csv)"
        cursor.execute(query)        
        logging.info("Inserted pushevents")
        query = f"COPY commit FROM '{file_name}_commits.csv' WITH (FORMAT csv)"
        cursor.execute(query)
        logging.info("Inserted commits")
        logging.info("Committing")
        conn.commit()
        cursor.close()
        conn.close()   
        logging.info("Done")  


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
    def getrecord(record: PushEvent) -> tuple:
        org_id = record.org.id if record.org else None
        org_login = record.org.login if record.org else None

        return (record.id, record.type, record.actor.id, record.actor.login, record.repo.id, 
                record.repo.name, record.payload.push_id, record.public, record.created_at,
                org_id, org_login)



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