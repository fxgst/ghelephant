import msgspec
from typing import Optional
from datetime import datetime


class Actor(msgspec.Struct):
    id: int
    login: str

class Author(msgspec.Struct):
    email: str
    name: str

class Repo(msgspec.Struct):
    id: int
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

class Org(msgspec.Struct):
    id: int
    login: str

class PushEvent(msgspec.Struct):
    id: str
    type: str
    actor: Actor
    repo: Repo
    payload: PushEventPayload
    public: bool
    created_at: datetime
    org: Optional[Org] = None
