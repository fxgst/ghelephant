import psycopg2
import json
from variables import database_name, database_user
from inserter import Inserter


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
        entry = json.loads(json_data)
        payload = entry['payload']

        Inserter.insert_actor(self.cursor, entry['actor'])

        # match entry['type']:
        #     case 'CommitCommentEvent':
        #         insert_commit_comment_event(payload)
        #     case 'CreateEvent':
        #         insert_create_event(payload)
        #     case 'DeleteEvent':
        #         insert_delete_event(payload)
        #     case 'ForkEvent':   
        #         insert_fork_event(payload)
        #     case 'GollumEvent':
        #         insert_gollum_event(payload)
        #     case 'IssueCommentEvent':
        #         insert_issue_comment_event(payload)
        #     case 'IssuesEvent':
        #         insert_issues_event(payload)
        #     case 'MemberEvent':
        #         insert_member_event(payload)
        #     case 'PublicEvent':
        #         insert_public_event(payload)
        #     case 'PullRequestEvent':
        #         insert_pull_request_event(payload)
        #     case 'PullRequestReviewCommentEvent':
        #         insert_pull_request_review_comment_event(payload)
        #     case 'PushEvent':
        #         insert_push_event(payload)
        #     case 'ReleaseEvent':
        #         insert_release_event(payload)
        #     case 'WatchEvent':
        #         insert_watch_event(payload)
        #     case _:
        #         logging.warning(f'Unknown event type: {entry['type']}')

    def create_tables(self):
        # NOTE: might not respect commits therein
        self.cursor.execute(open('database/create_tables.sql', 'r').read())
