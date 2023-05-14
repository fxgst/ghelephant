-- indices to speed up common queries. gets executed with option `-i`. only run after you are done 
-- adding data to the database.

ALTER TABLE archive ADD PRIMARY KEY (id);
create index archive_actor_login_idx on archive (actor_login);
create index archive_repo_name_idx on archive (repo_name);
create index archive_payload_id_idx on archive (payload_id);
create index archive_type_idx on archive (type);

create index issue_id_idx on issue (id);

create index issuecomment_comment_id_idx on issuecomment (comment_id);
create index issuecomment_issue_id_idx on issuecomment (issue_id);

-- created_at
create index archive_created_at_idx on archive (created_at);
create index releaseevent_created_at_idx on releaseevent (created_at);
create index forkevent_created_at_idx on forkevent (created_at);
create index issue_created_at_idx on issue (created_at);
create index issuecomment_created_at_idx on issuecomment (created_at);
create index pullrequest_created_at_idx on pullrequest (created_at);
create index pullrequestreviewcomment_created_at_idx on pullrequestreviewcomment (created_at);
