CREATE TABLE IF NOT EXISTS archive (
    id BIGINT PRIMARY KEY,
    type VARCHAR(29),
    actor_id BIGINT,
    actor_login VARCHAR(255),
    repo_id BIGINT,
    repo_name VARCHAR(255),
    payload JSONB,
    created_at TIMESTAMP,
    public BOOLEAN,
    org_id BIGINT,
    org_login VARCHAR(255)
);

-- CREATE TABLE IF NOT EXISTS actor (
--     id BIGINT PRIMARY KEY,
--     login VARCHAR(255),
--     name VARCHAR(255),
--     email VARCHAR(255)
-- );
--
-- CREATE TABLE IF NOT EXISTS repo (
--     id BIGINT PRIMARY KEY,
--     owner VARCHAR(255),
--     name VARCHAR(255)
-- );
