-- CREATE TABLE IF NOT EXISTS archive (
--     id BIGINT,
--     type VARCHAR(29),
--     actor_id BIGINT,
--     actor_login VARCHAR(255),
--     repo_id BIGINT,
--     repo_name VARCHAR(255),
--     payload JSONB,
--     public BOOLEAN,
--     created_at TIMESTAMP,
--     org_id BIGINT,
--     org_login VARCHAR(255)
-- ) WITHOUT OIDS;

CREATE TABLE IF NOT EXISTS archive (
    id BIGINT,
    type VARCHAR(29),
    actor_id BIGINT,
    actor_login VARCHAR(255),
    repo_id BIGINT,
    repo_name VARCHAR(255),
    payload_id BIGINT,
    public BOOLEAN,
    created_at TIMESTAMP,
    org_id BIGINT,
    org_login VARCHAR(255)
) WITHOUT OIDS;

CREATE TABLE IF NOT EXISTS commit (
    sha VARCHAR(40),
    push_id BIGINT,
    author_email VARCHAR(255),
    author_name VARCHAR(255),
    message TEXT,
    is_distinct BOOLEAN
) WITHOUT OIDS;

CREATE TABLE IF NOT EXISTS pushevent (
    id BIGINT,
    size INT,
    distinct_size INT,
    ref VARCHAR(255),
    head VARCHAR(40),
    before VARCHAR(40)
) WITHOUT OIDS;

CREATE TABLE IF NOT EXISTS commitcommentevent (
    id BIGINT,
    node_id VARCHAR(255),
    position INT NULL,
    line INT NULL,
    path VARCHAR(255) NULL,
    commit_id VARCHAR(40),
    author_association VARCHAR(63),
    body TEXT,
    reactions_total_count INT,
    reactions_plus_one INT,
    reactions_minus_one INT,
    reactions_laugh INT,
    reactions_hooray INT,
    reactions_confused INT,
    reactions_heart INT,
    reactions_rocket INT,
    reactions_eyes INT
) WITHOUT OIDS;

CREATE TABLE IF NOT EXISTS releaseevent (
    id BIGINT,
    node_id VARCHAR(255),
    tag_name VARCHAR(255),
    target_commitish VARCHAR(255),
    name VARCHAR(255),
    draft BOOLEAN,
    prerelease BOOLEAN,
    created_at TIMESTAMP,
    published_at TIMESTAMP,
    body TEXT
) WITHOUT OIDS;

CREATE TABLE IF NOT EXISTS deleteevent (
    event_id BIGINT,
    ref VARCHAR(255),
    ref_type VARCHAR(6),
    pusher_type VARCHAR(4)
) WITHOUT OIDS;

CREATE TABLE IF NOT EXISTS gollumevent (
    event_id BIGINT,
    page_name VARCHAR(255),
    title VARCHAR(255),
    summary TEXT,
    action VARCHAR(63),
    sha VARCHAR(40)
) WITHOUT OIDS;
