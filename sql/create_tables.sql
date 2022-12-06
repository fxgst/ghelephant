CREATE UNLOGGED TABLE IF NOT EXISTS archive (
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

CREATE UNLOGGED TABLE IF NOT EXISTS commit (
    sha VARCHAR(40),
    push_id BIGINT,
    author_email VARCHAR(255),
    author_name VARCHAR(255),
    message TEXT,
    is_distinct BOOLEAN
) WITHOUT OIDS;

CREATE UNLOGGED TABLE IF NOT EXISTS pushevent (
    id BIGINT,
    size INT,
    distinct_size INT,
    ref VARCHAR(255),
    head VARCHAR(40),
    before VARCHAR(40)
) WITHOUT OIDS;

CREATE UNLOGGED TABLE IF NOT EXISTS commitcommentevent (
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

CREATE UNLOGGED TABLE IF NOT EXISTS releaseevent (
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

CREATE UNLOGGED TABLE IF NOT EXISTS deleteevent (
    event_id BIGINT,
    ref VARCHAR(255),
    ref_type VARCHAR(6),
    pusher_type VARCHAR(4)
) WITHOUT OIDS;

CREATE UNLOGGED TABLE IF NOT EXISTS gollumevent (
    event_id BIGINT,
    page_name VARCHAR(255),
    title VARCHAR(255),
    summary TEXT,
    action VARCHAR(63),
    sha VARCHAR(40)
) WITHOUT OIDS;

CREATE UNLOGGED TABLE IF NOT EXISTS memberevent (
    event_id BIGINT,
    member_id BIGINT,
    login VARCHAR(255),
    node_id VARCHAR(255),
    type VARCHAR(4),
    site_admin BOOLEAN,
    action VARCHAR(5)
) WITHOUT OIDS;

CREATE UNLOGGED TABLE IF NOT EXISTS forkevent (
    forkee_id BIGINT,
    node_id VARCHAR(255),
    name VARCHAR(255),
    private BOOLEAN,
    owner_id BIGINT,
    owner_login VARCHAR(255),
    owner_node_id VARCHAR(255),
    owner_type VARCHAR(12),
    owner_site_admin BOOLEAN,
    description TEXT,
    fork BOOLEAN,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    pushed_at TIMESTAMP,
    homepage VARCHAR(255),
    size INT,
    stargazers_count INT,
    watchers_count INT,
    language VARCHAR(255),
    has_issues BOOLEAN,
    has_projects BOOLEAN,
    has_downloads BOOLEAN,
    has_wiki BOOLEAN,
    has_pages BOOLEAN,
    forks_count INT,
    archived BOOLEAN,
    disabled BOOLEAN,
    open_issues_count INT,
    allow_forking BOOLEAN,
    is_template BOOLEAN,
    web_commit_signoff_required BOOLEAN,
    topics TEXT,
    visibility VARCHAR(7),
    forks INT,
    open_issues INT,
    watchers INT,
    default_branch VARCHAR(255),
    public BOOLEAN,
    license_key VARCHAR(255),
    license_name VARCHAR(255),
    license_spdx_id VARCHAR(255),
    license_node_id VARCHAR(255)    
) WITHOUT OIDS;

CREATE UNLOGGED TABLE IF NOT EXISTS createevent (
    event_id BIGINT,
    ref VARCHAR(255),
    ref_type VARCHAR(10),
    master_branch VARCHAR(255),
    description TEXT,
    pusher_type VARCHAR(4)
) WITHOUT OIDS;

CREATE UNLOGGED TABLE IF NOT EXISTS issue (
    action VARCHAR(8),
    id BIGINT,
    node_id VARCHAR(255),
    number INT,
    title TEXT,
    user_login VARCHAR(255),
    user_id BIGINT,
    user_node_id VARCHAR(255),
    user_type VARCHAR(12),
    user_site_admin BOOLEAN,
    labels TEXT,
    state VARCHAR(6),
    locked BOOLEAN,
    assignee_id VARCHAR(255),
    assignees_ids VARCHAR(255),
    milestone_id VARCHAR(255),
    comments INT,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    closed_at TIMESTAMP,
    author_association VARCHAR(63),
    active_lock_reason VARCHAR(255),
    draft BOOLEAN,
    pull_request TEXT,
    body TEXT,
    reactions_total_count INT,
    reactions_plus_one INT,
    reactions_minus_one INT,
    reactions_laugh INT,
    reactions_hooray INT,
    reactions_confused INT,
    reactions_heart INT,
    reactions_rocket INT,
    reactions_eyes INT,
    performed_via_github_app VARCHAR(255),
    state_reason VARCHAR(255)
) WITHOUT OIDS;

CREATE UNLOGGED TABLE IF NOT EXISTS issuecomment (
    comment_id BIGINT,
    issue_id BIGINT,
    node_id VARCHAR(255),
    user_id BIGINT,
    user_login VARCHAR(255),
    user_node_id VARCHAR(255),
    user_type VARCHAR(12),
    user_site_admin BOOLEAN,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
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
    reactions_eyes INT,
    performed_via_github_app VARCHAR(255)
) WITHOUT OIDS;

CREATE UNLOGGED TABLE IF NOT EXISTS pullrequest (
    id BIGINT,
    action VARCHAR(8),
    number INT,
    node_id VARCHAR(255),
    state VARCHAR(6),
    locked BOOLEAN,
    title TEXT,
    user_login VARCHAR(255),
    user_id BIGINT,
    user_node_id VARCHAR(255),
    user_type VARCHAR(12),
    user_site_admin BOOLEAN,
    body TEXT,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    closed_at TIMESTAMP,
    merged_at TIMESTAMP,
    merge_commit_sha VARCHAR(40),
    assignee_id VARCHAR(255),
    assignees_ids VARCHAR(255),
    requested_reviewers_ids VARCHAR(255),
    requested_teams_ids VARCHAR(255),
    labels TEXT,
    milestone_id VARCHAR(255),
    draft BOOLEAN,
    author_association VARCHAR(63),
    active_lock_reason VARCHAR(63),
    merged BOOLEAN,
    mergeable BOOLEAN,
    mergeable_state VARCHAR(63),
    merged_by_id VARCHAR(255),
    comments INT,
    review_comments INT,
    maintainer_can_modify BOOLEAN,
    commits INT,
    additions INT,
    deletions INT,
    changed_files INT,
    head_repo_id BIGINT,
    head_repo_sha VARCHAR(40),
    base_repo_id BIGINT,
    base_repo_sha VARCHAR(40)
) WITHOUT OIDS;

CREATE UNLOGGED TABLE IF NOT EXISTS pullrequestreview (
    id BIGINT,
    action VARCHAR(8),
    node_id VARCHAR(255),
    user_id BIGINT,
    user_login VARCHAR(255),
    user_node_id VARCHAR(255),
    user_type VARCHAR(12),
    user_site_admin BOOLEAN,
    body TEXT,
    commit_id VARCHAR(40),
    submitted_at TIMESTAMP,
    state VARCHAR(31),
    author_association VARCHAR(63),
    pull_request_id BIGINT
) WITHOUT OIDS;
