from __future__ import annotations

from typing import Optional, List
from uuid import UUID, uuid4
from datetime import date, datetime
from pydantic import BaseModel, Field

from .desk import DeskBase


class ClassroomBase(BaseModel):
    id: UUID = Field(
        default_factory=uuid4,
        description="Persistent Classroom ID (server-generated).",
        json_schema_extra={"example": "550e8400-e29b-41d4-a716-446655440000"},
    )
    room_no: str = Field(
        ...,
        description="Room number.",
        json_schema_extra={"example": "502"},
    )
    building: str = Field(
        ...,
        description="Campus building name.",
        json_schema_extra={"example": "Northwest Corner Building"},
    )
    university: Optional[str] = Field(
        None,
        description="University name.",
        json_schema_extra={"example": "Columbia University"},
    )

    # Embed desks (each with persistent ID)
    desks: List[DeskBase] = Field(
        default_factory=list,
        description="Desks linked to this classroom (each carries a persistent Desk ID).",
        json_schema_extra={
            "example": [
                {
                    "id": "550e8400-e29b-41d4-a716-446655440001",
                    "label": "12H",
                    "hand_config": "Right",
                }
            ]
        },
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": "550e8400-e29b-41d4-a716-446655440000",
                    "room_no": "502",
                    "building": "Northwest Corner Building",
                    "university": "Columbia University",
                    "desks": [
                        {
                            "id": "550e8400-e29b-41d4-a716-446655440001",
                            "label": "12H",
                            "hand_config": "Right",
                        }
                    ],
                }
            ]
        }
    }


class ClassroomCreate(ClassroomBase):
    """Creation payload for a Classroom."""
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": "11111111-1111-4111-8111-111111111111",
                    "room_no": "417",
                    "building": "International Affairs Building",
                    "university": None,
                    "desks": [
                        {
                            "id": "11111111-1111-4111-8111-111111111112",
                            "label": "14G",
                            "hand_config": "Left",
                        }
                    ],
                }
            ]
        }
    }


class ClassroomUpdate(BaseModel):
    """Partial update; classroom ID is taken from the path, not the body."""
    room_no: Optional[str] = Field(
        None, description="Room number.", json_schema_extra={"example": "501"}
    )
    building: Optional[str] = Field(
        None, description="Campus building name.", json_schema_extra={"example": "Northwest Corner Building"}
    )
    university: Optional[str] = Field(
        None, description="University name.", json_schema_extra={"example": "Columbia University"}
    )
    desks: Optional[List[DeskBase]] = Field(
        None,
        description="Replace the entire set of desks with this list.",
        json_schema_extra={
            "example": [
                {
                    "id": "bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb",
                    "label": "4A",
                    "hand_config": "Left",
                }
            ]
        },
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "room_no": "501",
                    "building": "Northwest Corner Building",
                    "university": "Columbia University",
                },
                {"room_no": "602"},
                {
                    "desks": [
                        {
                            "id": "bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb",
                            "label": "4A",
                            "hand_config": "Left",
                        }
                    ]
                },
            ]
        }
    }


class ClassroomRead(ClassroomBase):
    """Server representation returned to clients."""
    id: UUID = Field(
        default_factory=uuid4,
        description="Server-generated Classroom ID.",
        json_schema_extra={"example": "99999999-9999-4999-8999-999999999999"},
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Creation timestamp (UTC).",
        json_schema_extra={"example": "2025-01-15T10:20:30Z"},
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Last update timestamp (UTC).",
        json_schema_extra={"example": "2025-01-16T12:00:00Z"},
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": "99999999-9999-4999-8999-999999999999",
                    "room_no": "502",
                    "building": "Northwest Corner Building",
                    "university": "Columbia University",
                    "desks": [
                        {
                            "id": "11111111-1111-4111-8111-111111111112",
                            "label": "14G",
                            "hand_config": "Left",
                        }
                    ],
                    "created_at": "2025-01-15T10:20:30Z",
                    "updated_at": "2025-01-16T12:00:00Z",
                }
            ]
        }
    }
