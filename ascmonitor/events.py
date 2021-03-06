""" Events which are put in the EventStore """
# pylint: disable=too-few-public-methods

from datetime import datetime
from enum import Enum
from typing import Any, Dict
import attr


class EventKind(Enum):
    """ Kind of an event """

    new_document = "new_document"
    updated_document = "updated_document"
    deleted_document = "deleted_document"
    post_start = "post_start"
    post_success = "post_success"
    post_failure = "post_failure"


def doc_for_event(document: Dict[str, Any]) -> Dict[str, Any]:
    """ Extract keys for event from document """
    keys = {"id", "title", "slug"}
    return {k: v for k, v in document.items() if k in keys}


def event_from_dict(event: Dict[str, Any]) -> "BaseEvent":
    """ Convert event dict to event """
    cls = globals()[event["class_name"]]
    del event["class_name"]
    del event["_id"]
    kind = EventKind(event["kind"])
    assert isinstance(cls, type(BaseEvent))
    return cls(**{**event, "kind": kind})  # type: ignore


@attr.s(frozen=True, auto_attribs=True)
class BaseEvent:
    """
    Base class for events.
    timestamps are in utc
    """

    document: Dict[str, Any] = attr.ib(converter=doc_for_event)
    kind: EventKind
    timestamp: datetime = attr.Factory(datetime.utcnow)

    def as_dict(self):
        """ Return as dict """
        dct = attr.asdict(self)
        dct["kind"] = self.kind.value
        dct["class_name"] = self.__class__.__name__
        return dct


@attr.s(frozen=True, auto_attribs=True)
class NewDocEvent(BaseEvent):
    """ Event """

    kind: EventKind = EventKind.new_document


@attr.s(frozen=True, auto_attribs=True)
class UpdatedDocEvent(BaseEvent):
    """ Event """

    kind: EventKind = EventKind.updated_document


@attr.s(frozen=True, auto_attribs=True)
class DeletedDocEvent(BaseEvent):
    """ Event """

    kind: EventKind = EventKind.deleted_document


@attr.s(frozen=True, auto_attribs=True)
class PostStartEvent(BaseEvent):
    """ Event """

    channel: str
    kind: EventKind = EventKind.post_start
    timestamp: datetime = attr.Factory(datetime.now)


@attr.s(frozen=True, auto_attribs=True)
class PostSuccessEvent(BaseEvent):
    """ Event """

    channel: str
    post: Dict[str, Any]
    kind: EventKind = EventKind.post_success
    timestamp: datetime = attr.Factory(datetime.now)


@attr.s(frozen=True, auto_attribs=True)
class PostFailureEvent(BaseEvent):
    """ Event """

    channel: str
    error: str
    allow_retry: bool
    kind: EventKind = EventKind.post_failure
    timestamp: datetime = attr.Factory(datetime.now)
