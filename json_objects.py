import msgspec
from typing import Optional
from datetime import datetime

# contains all the json objects from Events API/GH Archive.
# some of the objects are not used, but are included for completeness.


# common properties

class Actor(msgspec.Struct):
    id: int
    login: str


class Repo(msgspec.Struct):
    id: int
    name: str


class Org(msgspec.Struct):
    id: int
    login: str


class GenericEvent(msgspec.Struct):
    id: str
    type: str
    actor: Actor
    repo: Repo
    public: bool
    created_at: datetime
    org: Optional[Org] = None


# PushEvent

class Author(msgspec.Struct):
    email: str
    name: str


class Commit(msgspec.Struct):
    sha: str
    author: Author
    message: str
    distinct: bool


class PushEventPayload(msgspec.Struct):
    push_id: int
    size: int
    distinct_size: int
    ref: str
    head: str
    before: str
    commits: list[Commit]


class PushEvent(msgspec.Struct):
    payload: PushEventPayload


# CommitCommentEvent

class Comment(msgspec.Struct):
    id: int
    commit_id: str
    body: str
    author_association: Optional[str] = None
    position: Optional[int] = None
    line: Optional[int] = None
    path: Optional[str] = None


class CommitCommentEventPayload(msgspec.Struct):
    comment: Comment


class CommitCommentEvent(msgspec.Struct):
    payload: CommitCommentEventPayload


# ReleaseEvent

class Release(msgspec.Struct):
    id: int
    tag_name: str
    target_commitish: str
    draft: bool
    prerelease: bool
    created_at: datetime
    published_at: Optional[datetime] = None
    body: Optional[str] = None
    name: Optional[str] = None


class ReleaseEventPayload(msgspec.Struct):
    release: Release


class ReleaseEvent(msgspec.Struct):
    payload: ReleaseEventPayload


# DeleteEvent

class DeleteEventPayload(msgspec.Struct):
    ref: str
    ref_type: str
    pusher_type: str


class DeleteEvent(msgspec.Struct):
    payload: DeleteEventPayload


# GollumEvent

class Page(msgspec.Struct):
    page_name: str
    title: str
    action: str
    sha: str
    summary: Optional[str] = None


class GollumEventPayload(msgspec.Struct):
    pages: list[Page]


class GollumEvent(msgspec.Struct):
    payload: GollumEventPayload


# MemberEvent

class Member(msgspec.Struct):
    id: int
    login: str
    type: str
    site_admin: bool

class MemberEventPayload(msgspec.Struct):
    action: str
    member: Member


class MemberEvent(msgspec.Struct):
    payload: MemberEventPayload


# ForkEvent

class License(msgspec.Struct):
    key: str
    name: str
    spdx_id: Optional[str] = None


class Forkee(msgspec.Struct):
    id: int
    name: str
    private: bool
    owner: Member
    fork: bool
    created_at: datetime
    updated_at: datetime
    pushed_at: datetime
    size: int
    stargazers_count: int
    watchers_count: int
    has_issues: bool
    has_downloads: bool
    has_wiki: bool
    forks_count: int
    open_issues_count: int 
    forks: int
    open_issues: int
    watchers: int
    default_branch: str
    has_pages: Optional[bool] = None
    has_projects: Optional[bool] = None
    archived: Optional[bool] = None
    visibility: Optional[str] = None
    topics: Optional[list[str]] = None
    web_commit_signoff_required: Optional[bool] = None
    is_template: Optional[bool] = None
    allow_forking: Optional[bool] = None
    disabled: Optional[bool] = None
    public: Optional[bool] = None
    description: Optional[str] = None
    homepage: Optional[str] = None
    language: Optional[str] = None
    license: Optional[License] = None


class ForkEventPayload(msgspec.Struct):
    forkee: Forkee


class ForkEvent(msgspec.Struct):
    payload: ForkEventPayload


# CreateEvent

class CreateEventPayload(msgspec.Struct):
    ref_type: str
    master_branch: str
    pusher_type: str
    description: Optional[str] = None
    ref: Optional[str] = None

class CreateEvent(msgspec.Struct):
    payload: CreateEventPayload


# PullRequestEvent

class PullRequestHead(msgspec.Struct):
    sha: str
    repo: Optional[Forkee]

class Label(msgspec.Struct):
    name: str

class Milestone(msgspec.Struct):
    id: int

class Team(msgspec.Struct):
    name: str
    
class PullRequest(msgspec.Struct):
    id: int
    number: int
    state: str
    locked: bool
    title: str
    user: Member
    head: PullRequestHead
    base: PullRequestHead
    body: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    closed_at: Optional[datetime] = None
    merged_at: Optional[datetime] = None
    merge_commit_sha: Optional[str] = None
    assignee: Optional[Member] = None
    assignees: Optional[list[Member]] = None
    requested_reviewers: Optional[list[Member]] = None
    requested_teams: Optional[list[Team]] = None
    labels: Optional[list[Label]] = None
    milestone: Optional[Milestone] = None
    draft: Optional[bool] = None
    author_association: Optional[str] = None
    active_lock_reason: Optional[str] = None
    merged: Optional[bool] = None
    mergeable: Optional[bool] = None
    rebaseable: Optional[bool] = None
    mergeable_state: Optional[str] = None
    merged_by: Optional[Member] = None
    comments: Optional[int] = None
    review_comments: Optional[int] = None
    maintainer_can_modify: Optional[bool] = None
    commits: Optional[int] = None
    additions: Optional[int] = None
    deletions: Optional[int] = None
    changed_files: Optional[int] = None

class PullRequestEventPayload(msgspec.Struct):
    action: str
    number: int
    pull_request: PullRequest

class PullRequestEvent(msgspec.Struct):
    payload: PullRequestEventPayload


# PullRequestReviewEvent

class Review(msgspec.Struct):
    id: int
    user: Member
    commit_id: str
    submitted_at: datetime
    state: str
    author_association: str
    body: Optional[str] = None
    
class PullRequestReviewEventPayload(msgspec.Struct):
    action: str
    review: Review
    pull_request: PullRequest

class PullRequestReviewEvent(msgspec.Struct):
    payload: PullRequestReviewEventPayload


# PullRequestReviewCommentEvent

class PullRequestReviewCommentEventPayload(msgspec.Struct):
    action: str
    pull_request: PullRequest

class PullRequestReviewCommentEvent(msgspec.Struct):
    payload: PullRequestReviewCommentEventPayload