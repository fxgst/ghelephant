CREATE TABLE IF NOT EXISTS archive (
    id BIGINT,
    type VARCHAR(29),
    actor_id BIGINT,
    actor_login VARCHAR(255),
    repo_id BIGINT,
    repo_name VARCHAR(255),
    push_id BIGINT,
    public BOOLEAN,
    created_at TIMESTAMP,
    org_id BIGINT,
    org_login VARCHAR(255)
) WITHOUT OIDS;

CREATE TABLE IF NOT EXISTS pushevent (
    push_id BIGINT,
    size INT,
    distinct_size INT,
    ref VARCHAR(255),
    head VARCHAR(40),
    before VARCHAR(40)
) WITHOUT OIDS;

CREATE TABLE IF NOT EXISTS commit (
    sha VARCHAR(40),
    push_id BIGINT,
    author_email VARCHAR(255),
    author_name VARCHAR(255),
    message TEXT,
    is_distinct BOOLEAN
) WITHOUT OIDS;
