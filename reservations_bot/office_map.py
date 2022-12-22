from enum import Enum
from typing import Set, Dict

from reservations_bot.models import get_all_reserved_workspaces_for_date, WorkspaceID

OFFICE_MAP = """
🏙        🏙🏙         🏙

{ws_1}1    3{ws_3}️{ws_5}5    7{ws_7}️

{ws_2}2    4{ws_4}️{ws_6}6    8{ws_8}️

✖        ✖ ✖️      9{ws_9}️
"""


WORKSPACES = [
    1, 3, 5, 7,
    2, 4, 6, 8,
    9,
]


ATTACHED_WORKSPACES = [1, 2, 3, 4, 7]


class Status(Enum):
    AVAILABLE = 1
    RESERVED = 2
    ATTACHED = 3
    INACTIVE = 4
    ACTIVE = 5


EMOJI = {
    Status.AVAILABLE: "🟩",
    Status.RESERVED: "🟥",
    Status.ATTACHED: "🟨",
    Status.INACTIVE: "⬜️",
    Status.ACTIVE: "🟦",
}


def get_workspace_statuses_for_date(date, explicit: Dict[WorkspaceID, Status] = None) -> Dict[WorkspaceID, Status]:
    if explicit is None:
        explicit = {}

    statuses: Dict[WorkspaceID, Status] = {}

    reserved_workspaces: Set[int] = get_all_reserved_workspaces_for_date(date)

    for workspace in WORKSPACES:
        if workspace in explicit:
            statuses[workspace] = explicit.get(workspace)

        elif workspace in reserved_workspaces:
            statuses[workspace] = Status.RESERVED

        elif workspace in ATTACHED_WORKSPACES:
            statuses[workspace] = Status.ATTACHED

        else:
            statuses[workspace] = Status.AVAILABLE

    return statuses


def get_statuses_with_highlighted_workspace(workspace_to_highlight: WorkspaceID) -> Dict[WorkspaceID, Status]:
    statuses: Dict[WorkspaceID, Status] = {}

    for workspace in WORKSPACES:
        statuses[workspace]: Status = Status.ACTIVE if workspace == workspace_to_highlight else Status.INACTIVE

    return statuses


def get_office_map(statuses: Dict[WorkspaceID, Status]) -> str:
    format_args: Dict = {}

    for workspace, status in statuses.items():
        format_args[f"ws_{workspace}"] = EMOJI.get(status)

    return OFFICE_MAP.format(**format_args)
