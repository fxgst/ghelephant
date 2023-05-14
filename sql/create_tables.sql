-- creates all the tables and types needed. gets executed automatically when GH Elephant is first run to create a database.

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'eventtype') THEN
        CREATE TYPE eventtype AS ENUM ('CommitCommentEvent',
            'CreateEvent',
            'DeleteEvent',
            'ForkEvent',
            'GollumEvent',
            'IssueCommentEvent',
            'IssuesEvent',
            'MemberEvent',
            'PublicEvent',
            'PullRequestEvent',
            'PullRequestReviewCommentEvent',
            'PullRequestReviewEvent',
            'PushEvent',
            'ReleaseEvent',
            'WatchEvent'
        );
        CREATE TYPE issuestate AS ENUM ('closed', 'open');
        CREATE TYPE usertype AS ENUM ('Bot', 'Mannequin', 'Organization', 'User');
        CREATE TYPE authorassociation AS ENUM ('COLLABORATOR', 'CONTRIBUTOR', 'MANNEQUIN', 'MEMBER', 'NONE', 'OWNER');
        CREATE TYPE actiontype AS ENUM ('closed', 'created', 'opened', 'reopened', 'edited', 'added');
        CREATE TYPE prrstate AS ENUM ('approved', 'changes_requested', 'commented', 'dismissed');
        CREATE TYPE reftype AS ENUM ('branch', 'tag', 'repository');
        CREATE TYPE pushertype AS ENUM ('deploy_key', 'user');
        CREATE TYPE visibilitytype AS ENUM ('public', 'private');
        CREATE TYPE sidetype AS ENUM ('LEFT', 'RIGHT');
        CREATE TYPE activelockreasontype AS ENUM ('off-topic', 'resolved', 'spam', 'too heated');
        CREATE TYPE mergeablestatetype AS ENUM ('clean', 'dirty', 'unknown', 'unstable', 'draft');
    END IF;
END $$;

CREATE UNLOGGED TABLE IF NOT EXISTS archive (
    id BIGINT,
    type eventtype,
    actor_id BIGINT,
    actor_login VARCHAR(255),
    repo_id BIGINT,
    repo_name VARCHAR(255),
    payload_id BIGINT,
    created_at TIMESTAMP,
    org_id BIGINT,
    org_login VARCHAR(255)
) WITHOUT OIDS;

CREATE UNLOGGED TABLE IF NOT EXISTS commit (
    sha VARCHAR(40),
    push_id BIGINT,
    author_email VARCHAR(127),
    author_name VARCHAR(127),
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
    position INT,
    line INT,
    path VARCHAR(255),
    commit_id VARCHAR(40),
    author_association authorassociation,
    body TEXT
) WITHOUT OIDS;

CREATE UNLOGGED TABLE IF NOT EXISTS releaseevent (
    id BIGINT,
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
    ref_type reftype,
    pusher_type pushertype
) WITHOUT OIDS;

CREATE UNLOGGED TABLE IF NOT EXISTS gollumevent (
    event_id BIGINT,
    page_name VARCHAR(255),
    title VARCHAR(255),
    summary TEXT,
    action actiontype,
    sha VARCHAR(40)
) WITHOUT OIDS;

CREATE UNLOGGED TABLE IF NOT EXISTS memberevent (
    event_id BIGINT,
    member_id BIGINT,
    login VARCHAR(255),
    type usertype,
    site_admin BOOLEAN,
    action actiontype
) WITHOUT OIDS;

CREATE UNLOGGED TABLE IF NOT EXISTS forkevent (
    forkee_id BIGINT,
    name VARCHAR(255),
    private BOOLEAN,
    owner_id BIGINT,
    owner_login VARCHAR(255),
    owner_type usertype,
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
    language VARCHAR(127),
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
    visibility visibilitytype,
    forks INT,
    open_issues INT,
    watchers INT,
    default_branch VARCHAR(255),
    public BOOLEAN,
    license_key VARCHAR(255),
    license_name VARCHAR(255),
    license_spdx_id VARCHAR(255)
) WITHOUT OIDS;

CREATE UNLOGGED TABLE IF NOT EXISTS createevent (
    event_id BIGINT,
    ref VARCHAR(127),
    ref_type reftype,
    master_branch VARCHAR(127),
    description TEXT,
    pusher_type pushertype
) WITHOUT OIDS;

CREATE UNLOGGED TABLE IF NOT EXISTS issue (
    action actiontype,
    id BIGINT,
    number INT,
    title TEXT,
    user_login VARCHAR(255),
    user_id BIGINT,
    user_type usertype,
    user_site_admin BOOLEAN,
    labels TEXT,
    state issuestate,
    locked BOOLEAN,
    assignee_id VARCHAR(255),
    assignees_ids VARCHAR(255),
    milestone_id VARCHAR(255),
    comments INT,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    closed_at TIMESTAMP,
    author_association authorassociation,
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
    user_type usertype,
    user_site_admin BOOLEAN,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    author_association authorassociation,
    body TEXT,
    -- reactions *almost always* 0
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
    action actiontype,
    number INT,
    state issuestate,
    locked BOOLEAN,
    title TEXT,
    user_login VARCHAR(255),
    user_id BIGINT,
    user_type usertype,
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
    author_association authorassociation,
    active_lock_reason activelockreasontype,
    merged BOOLEAN,
    mergeable BOOLEAN,
    mergeable_state mergeablestatetype,
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
    action actiontype,
    user_id BIGINT,
    user_login VARCHAR(255),
    user_type usertype,
    user_site_admin BOOLEAN,
    body TEXT,
    commit_id VARCHAR(40),
    submitted_at TIMESTAMP,
    state prrstate,
    author_association authorassociation,
    pull_request_id BIGINT
) WITHOUT OIDS;

CREATE UNLOGGED TABLE IF NOT EXISTS pullrequestreviewcomment (
    id BIGINT,
    pull_request_review_id BIGINT,
    diff_hunk TEXT,
    path TEXT,
    position INT,
    original_position INT,
    commit_id VARCHAR(40),
    original_commit_id VARCHAR(40),
    user_id BIGINT,
    user_login VARCHAR(255),
    user_type usertype,
    user_site_admin BOOLEAN,
    body TEXT,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    author_association authorassociation,
    reactions_total_count INT,
    reactions_plus_one INT,
    reactions_minus_one INT,
    reactions_laugh INT,
    reactions_hooray INT,
    reactions_confused INT,
    reactions_heart INT,
    reactions_rocket INT,
    reactions_eyes INT,
    start_line INT,
    original_start_line INT,
    start_side sidetype,
    line INT,
    original_line INT,
    side sidetype,
    in_reply_to_id BIGINT,
    pull_request_id BIGINT
) WITHOUT OIDS;
