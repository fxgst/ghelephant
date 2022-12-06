from json_objects import *
import orjson
import logging


class JSONToCSVConverter:
    def __init__(self, writers) -> None:
        self.writers = writers

    def write_events(self, f):
        added_ids = set()
        added_pushes = set()

        for line in f:
            try:
                generic_event = msgspec.json.decode(line, type=GenericEvent)
            except msgspec.ValidationError:
                logging.error(f"Malformed event: {line}")
                continue

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
                case 'ForkEvent':
                    self.write_fork_event(line, generic_event)
                case 'CreateEvent':
                    self.write_create_event(line, generic_event)
                case 'IssuesEvent':
                    self.write_issues_event(line, generic_event)
                case 'IssueCommentEvent':
                    self.write_issue_comment_event(line, generic_event)
                case 'PullRequestEvent':
                    self.write_pull_request_event(line, generic_event)
                case _:
                    # logging.error(f'Unknown event type: {generic_event.type}')
                    pass

    def write_pull_request_event(self, line: bytes, generic_event: GenericEvent):
        record = msgspec.json.decode(line, type=PullRequestEvent)
        self.writers.archive.writerow(self.generic_event_tuple(generic_event, record.payload.pull_request.id))
        pr = record.payload.pull_request
        assignee = pr.assignee.id if pr.assignee else None
        assignees = [a.id for a in pr.assignees] if pr.assignees else None
        requested_reviewers = [r.id for r in pr.requested_reviewers] if pr.requested_reviewers else None
        requested_teams = [t.name for t in pr.requested_teams] if pr.requested_teams else None
        milestone = pr.milestone.id if pr.milestone else None
        labels = [l.name for l in pr.labels] if pr.labels else None
        head_repo = pr.head.repo.id if pr.head.repo else None
        base_repo = pr.base.repo.id if pr.base.repo else None
        self.writers.pullrequest.writerow((pr.id, record.payload.action, record.payload.number, pr.node_id, pr.state, pr.locked, pr.title,
                                           pr.user.login, pr.user.id, pr.user.node_id, pr.user.type, pr.user.site_admin, pr.body,
                                           pr.created_at, pr.updated_at, pr.closed_at, pr.merged_at, pr.merge_commit_sha, assignee, assignees, 
                                           str(requested_reviewers)[:255], str(requested_teams)[:255], labels, milestone, pr.draft, pr.author_association,
                                           pr.active_lock_reason, pr.merged, pr.mergeable, pr.mergeable_state, pr.merged_by.id if pr.merged_by else None,
                                           pr.comments, pr.review_comments, pr.maintainer_can_modify, pr.commits, pr.additions, pr.deletions, pr.changed_files,
                                           head_repo, pr.head.sha, base_repo, pr.base.sha))

    def write_issue_comment_event(self, line: bytes, generic_event: GenericEvent):
        record = orjson.loads(line)
        c = record['payload']['comment']
        comment_id = c['id']
        issue_id = record['payload']['issue']['id']

        self.writers.archive.writerow(self.generic_event_tuple(generic_event, comment_id))
        self.writers.issue.writerow(self.issue_event_tuple(record))
        app = c['performed_via_github_app']['slug'] if c['performed_via_github_app'] else None
        self.writers.issuecomment.writerow((comment_id, issue_id, c['node_id'], c['user']['id'], c['user']['login'],
                                            c['user']['node_id'], c['user']['type'], c['user']['site_admin'],
                                            c['created_at'], c['updated_at'], c['author_association'], c['body'],
                                            c['reactions']['total_count'], c['reactions']['+1'],
                                            c['reactions']['-1'], c['reactions']['laugh'], c['reactions']['hooray'],
                                            c['reactions']['confused'], c['reactions']['heart'], 
                                            c['reactions']['rocket'], c['reactions']['eyes'], app))

    def issue_event_tuple(self, record):
        i = record['payload']['issue']
        assignee = i['assignee']['id'] if i['assignee'] else None
        milestone = i['milestone']['id'] if i['milestone'] else None
        app = i['performed_via_github_app']['slug'] if i['performed_via_github_app'] else None
        assignees_ids = [a['id'] for a in i['assignees']] if i['assignees'] else None
        labels_names = [l['name'] for l in i['labels']] if i['labels'] else None
        draft = i['draft'] if 'draft' in i else None
        pull_request = i['pull_request'] if 'pull_request' in i else None
        return (record['payload']['action'], i['id'], i['node_id'], i['number'], i['title'],
                i['user']['login'], i['user']['id'], i['user']['node_id'], i['user']['type'],
                i['user']['site_admin'], labels_names, i['state'], i['locked'], assignee, assignees_ids,
                milestone, i['comments'], i['created_at'], i['updated_at'], i['closed_at'],
                i['author_association'], i['active_lock_reason'], draft, pull_request, i['body'],
                i['reactions']['total_count'], i['reactions']['+1'], i['reactions']['-1'], i['reactions']['laugh'],
                i['reactions']['hooray'], i['reactions']['confused'], i['reactions']['heart'],
                i['reactions']['rocket'], i['reactions']['eyes'], app, i['state_reason'])

    def write_issues_event(self, line: bytes, generic_event: GenericEvent):
        record = orjson.loads(line)
        issue_id = record['payload']['issue']['id']
        self.writers.archive.writerow(self.generic_event_tuple(generic_event, issue_id))
        self.writers.issue.writerow(self.issue_event_tuple(record))

    def write_create_event(self, line: bytes, generic_event: GenericEvent):
        record = msgspec.json.decode(line, type=CreateEvent)
        self.writers.archive.writerow(self.generic_event_tuple(generic_event))
        ref = record.payload.ref[:255] if record.payload.ref else None
        self.writers.createevent.writerow((generic_event.id, ref, record.payload.ref_type,
                                           record.payload.master_branch[:255], record.payload.description,
                                           record.payload.pusher_type))

    def write_fork_event(self, line: bytes, generic_event: GenericEvent):
        record = msgspec.json.decode(line, type=ForkEvent)
        f = record.payload.forkee
        license_key = f.license.key if f.license else None
        license_name = f.license.name if f.license else None
        license_spdx_id = f.license.spdx_id if f.license else None
        license_node_id = f.license.node_id if f.license else None
        self.writers.archive.writerow(self.generic_event_tuple(generic_event, f.id))
        self.writers.forkevent.writerow((f.id, f.node_id, f.name, f.private, f.owner.id, f.owner.login,
                                         f.owner.node_id, f.owner.type, f.owner.site_admin, f.description, f.fork,
                                         f.created_at,
                                         f.updated_at, f.pushed_at, f.homepage, f.size, f.stargazers_count,
                                         f.watchers_count,
                                         f.language, f.has_issues, f.has_projects, f.has_downloads, f.has_wiki,
                                         f.has_pages,
                                         f.forks_count, f.archived, f.disabled, f.open_issues_count, f.allow_forking,
                                         f.is_template, f.web_commit_signoff_required, f.topics, f.visibility, f.forks,
                                         f.open_issues, f.watchers,
                                         f.default_branch, f.public, license_key,
                                         license_name, license_spdx_id, license_node_id))

    def write_member_event(self, line: bytes, generic_event: GenericEvent):
        record = msgspec.json.decode(line, type=MemberEvent)
        self.writers.archive.writerow(self.generic_event_tuple(generic_event))
        self.writers.memberevent.writerow((generic_event.id, record.payload.member.id,
                                           record.payload.member.login, record.payload.member.node_id,
                                           record.payload.member.type, record.payload.member.site_admin,
                                           record.payload.action))

    def write_gollum_event(self, line: bytes, generic_event: GenericEvent):
        record = msgspec.json.decode(line, type=GollumEvent)
        self.writers.archive.writerow(self.generic_event_tuple(generic_event))
        for page in record.payload.pages:
            self.writers.gollumevent.writerow(
                (generic_event.id, page.page_name, page.title, page.summary, page.action, page.sha))

    def write_delete_event(self, line: bytes, generic_event: GenericEvent):
        record = msgspec.json.decode(line, type=DeleteEvent)
        self.writers.archive.writerow(self.generic_event_tuple(generic_event))
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
                                         record.payload.distinct_size, record.payload.ref[:255],
                                         record.payload.head, record.payload.before))
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
