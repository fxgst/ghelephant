from json_objects import *
import orjson


class JSONToCSVConverter:
    def __init__(self, writers) -> None:
        self.writers = writers

    def write_events(self, f):
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
                    self.write_push_event(record, generic_event)
                case 'CommitCommentEvent':
                    self.write_commit_comment_event(line, generic_event)
                case 'WatchEvent':
                    self.write_generic_event(generic_event)
                case 'ReleaseEvent':
                    self.write_release_event(line, generic_event)
                case 'DeleteEvent':
                    self.write_delete_event(line, generic_event)
                case 'GollumEvent':
                    self.write_gollum_event(line, generic_event)
                case 'PublicEvent':
                    self.write_generic_event(generic_event)
                case 'MemberEvent':
                    self.write_member_event(line, generic_event)
                case _:
                    pass

    def write_member_event(self, line: bytes, generic_event: GenericEvent):
        record = msgspec.json.decode(line, type=MemberEvent)
        self.writers.archive.writerow(self.generic_event_tuple(generic_event, generic_event.id))
        self.writers.memberevent.writerow((generic_event.id, record.payload.member.id,
                                           record.payload.member.login, record.payload.member.node_id,
                                           record.payload.member.type, record.payload.member.site_admin,
                                           record.payload.action))

    def write_gollum_event(self, line: bytes, generic_event: GenericEvent):
        record = msgspec.json.decode(line, type=GollumEvent)
        self.writers.archive.writerow(self.generic_event_tuple(generic_event, generic_event.id))
        for page in record.payload.pages:
            self.writers.gollumevent.writerow(
                (generic_event.id, page.page_name, page.title, page.summary, page.action, page.sha))

    def write_delete_event(self, line: bytes, generic_event: GenericEvent):
        record = msgspec.json.decode(line, type=DeleteEvent)
        self.writers.archive.writerow(self.generic_event_tuple(generic_event, generic_event.id))
        self.writers.deleteevent.writerow((generic_event.id, record.payload.ref[:255], record.payload.ref_type,
                                           record.payload.pusher_type))

    def write_release_event(self, line: bytes, generic_event: GenericEvent):
        record = msgspec.json.decode(line, type=ReleaseEvent)
        release = record.payload.release
        self.writers.archive.writerow(self.generic_event_tuple(generic_event, release.id))
        self.writers.releaseevent.writerow((release.id, release.node_id, release.tag_name,
                                            release.target_commitish, release.name, release.draft, release.prerelease,
                                            release.created_at, release.published_at, release.body))

    def write_push_event(self, record: PushEvent, generic_event: GenericEvent):
        self.writers.archive.writerow(self.generic_event_tuple(generic_event, record.payload.push_id))
        self.writers.pushevent.writerow((record.payload.push_id, record.payload.size,
                                         record.payload.distinct_size, record.payload.ref[:255], record.payload.head,
                                         record.payload.before))
        for commit in record.payload.commits:
            self.writers.commit.writerow((commit.sha, record.payload.push_id,
                                          commit.author.email[:255], commit.author.name[:255], commit.message,
                                          commit.distinct))

    def write_commit_comment_event(self, line: bytes, generic_event: GenericEvent):
        record = orjson.loads(line)
        c = record['payload']['comment']
        self.writers.archive.writerow(self.generic_event_tuple(generic_event, c['id']))
        self.writers.commitcommentevent.writerow((c['id'], c['node_id'], c['position'], c['line'],
                                                  c['path'], c['commit_id'], c['author_association'], c['body'],
                                                  c['reactions']['total_count'], c['reactions']['+1'],
                                                  c['reactions']['-1'],
                                                  c['reactions']['laugh'], c['reactions']['hooray'],
                                                  c['reactions']['confused'],
                                                  c['reactions']['heart'], c['reactions']['rocket'],
                                                  c['reactions']['eyes']))

    def write_generic_event(self, generic_event: GenericEvent):
        self.writers.archive.writerow(self.generic_event_tuple(generic_event))

    def generic_event_tuple(self, record: GenericEvent, payload_id=None) -> tuple:
        org_id = record.org.id if record.org else None
        org_login = record.org.login if record.org else None
        return (record.id, record.type, record.actor.id, record.actor.login, record.repo.id,
                record.repo.name, payload_id, record.public, record.created_at,
                org_id, org_login)
