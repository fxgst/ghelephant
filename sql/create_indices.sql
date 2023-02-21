-- archive
create index archive_id_idx on archive (id);
create index archive_actor_login_idx on archive (actor_login);
create index archive_repo_name_idx on archive (repo_name);
-- created_at
create index archive_created_at_idx on archive (created_at);
create index releaseevent_created_at_idx on releaseevent (created_at);
create index forkevent_created_at_idx on forkevent (created_at);
create index issue_created_at_idx on issue (created_at);
create index issuecomment_created_at_idx on issuecomment (created_at);
create index pullrequest_created_at_idx on pullrequest (created_at);
create index pullrequestreviewcomment_created_at_idx on pullrequestreviewcomment (created_at);
