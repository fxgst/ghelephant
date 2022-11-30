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
