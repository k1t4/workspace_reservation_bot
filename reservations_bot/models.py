import datetime as dt
from typing import Dict, Optional, List, Set, Match

import redis

import settings
import re

redis_client = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, decode_responses=True)

WorkspaceID = int
Reservations = Dict[dt.date, WorkspaceID]


class UserException(Exception):
    pass


class User:
    def __init__(self, telegram_id: int, name: str):
        self.telegram_id: int = telegram_id
        self.name: str = name
        self._redis_key: str = f"users:{telegram_id}"

    def get_reservations(self) -> Reservations:
        reservations: Reservations = {}

        user_reservations_keys: List[str] = redis_client.keys(f"{self._redis_key}:*")

        for key in user_reservations_keys:
            workspace_id: WorkspaceID = int(redis_client.get(key))
            date: dt.date = get_date_from_key(key)

            reservations[date] = workspace_id

        return reservations

    def get_reserved_workspace(self, date: dt.date) -> Optional[WorkspaceID]:
        key: str = f"{self._redis_key}:{date.isoformat()}"
        workspace_id: Optional[WorkspaceID] = redis_client.get(key)

        if workspace_id:
            return int(workspace_id)

    def add_reservation(self, date: dt.date, workspace_id: WorkspaceID) -> None:
        if self.has_reservation_on_date(date):
            raise UserException("User already has reservation for this date")

        key: str = f"{self._redis_key}:{date.isoformat()}"
        redis_client.set(key, workspace_id)

        expiration_datetime: dt.datetime = dt.datetime.combine(date, time=dt.time.min)
        redis_client.expireat(key, expiration_datetime)

    def remove_reservation(self, date: dt.date) -> None:
        key: str = f"{self._redis_key}:{date.isoformat()}"
        was_removed: int = redis_client.delete(key)

        if not was_removed:
            raise UserException("No reservation to delete")

    def has_reservations(self) -> bool:
        pattern: str = f"{self._redis_key}:*"
        return bool(redis_client.keys(pattern))

    def has_reservation_on_date(self, date: dt.date) -> bool:
        key: str = f"{self._redis_key}:{date.isoformat()}"
        return bool(redis_client.exists(key))


def get_date_from_key(key: str) -> Optional[dt.date]:
    pattern: str = r"users:\d+:(\S+)"
    match: Optional[Match] = re.search(pattern, key)

    if match:
        date: str = match.groups()[0]
        return dt.date.fromisoformat(date)


def get_all_reserved_workspaces_for_date(date: dt.date) -> Set[int]:
    pattern = f"users:*:{date.isoformat()}"
    keys: List[str] = redis_client.keys(pattern)

    reserved_workspaces: Set[int] = set()

    for key in keys:
        workspace_id: WorkspaceID = int(redis_client.get(key))
        reserved_workspaces.add(workspace_id)

    return reserved_workspaces
