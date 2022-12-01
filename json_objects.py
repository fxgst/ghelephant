import msgspec
from typing import Optional
from datetime import datetime


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

class Reactions(msgspec.Struct):
    total_count: int
    # plus_one: int
    # minus_one: int
    laugh: int
    hooray: int
    confused: int
    heart: int
    rocket: int
    eyes: int


class Comment(msgspec.Struct):
    id: int
    node_id: str
    commit_id: str
    author_association: str
    body: str
    reactions: Reactions
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
    node_id: str
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
    node_id: str
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
    spdx_id: str
    node_id: str


class Forkee(msgspec.Struct):
    id: int
    node_id: str
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
    has_projects: bool
    has_downloads: bool
    has_wiki: bool
    has_pages: bool
    forks_count: int
    archived: bool
    disabled: bool
    open_issues_count: int 
    allow_forking: bool
    is_template: bool
    web_commit_signoff_required: bool
    topics: list[str]
    visibility: str
    forks: int
    open_issues: int
    watchers: int
    default_branch: str
    public: bool
    description: Optional[str] = None
    homepage: Optional[str] = None
    language: Optional[str] = None
    license: Optional[License] = None


class ForkEventPayload(msgspec.Struct):
    forkee: Forkee


class ForkEvent(msgspec.Struct):
    payload: ForkEventPayload