-- ALTER TABLE archive ADD PRIMARY KEY (id);
create index archive_id_idx on archive (id);
create index archive_created_at_idx on archive (created_at);
create index issue_created_at_idx on issue (created_at);
