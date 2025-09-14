from __future__ import annotations

from typing import Optional, Annotated
from uuid import UUID, uuid4
from datetime import datetime
from pydantic import BaseModel, Field, StringConstraints

# Desk Configuration based on being Left-Handed or Right-Handed
DeskConfig = Annotated[str, StringConstraints(pattern=r"^(Left|Right)$")]


class DeskBase(BaseModel):
    id: UUID = Field(
        default_factory=uuid4,
        description="Persistent Desk ID (server-generated).",
        json_schema_extra={"example": "550e8400-e29b-41d4-a716-446655440001"},
    )
    label: str = Field(
        ...,
        description="Desk label.",
        json_schema_extra={"example": "12H"},
    )
    hand_config: DeskConfig = Field(
        ...,
        description="Left or Right desk configuration.",
        json_schema_extra={"example": "Right"},
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": "550e8400-e29b-41d4-a716-446655440000",
                    "label": "12H",
                    "hand_config": "Right",
                }
            ]
        }
    }


class DeskCreate(DeskBase):
    """Creation payload; ID is generated server-side but present in the base model."""
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": "11111111-1111-4111-8111-111111111112",
                    "label": "14G",
                    "hand_config": "Left",
                }
            ]
        }
    }


class DeskUpdate(BaseModel):
    """Partial update for a Desk; supply only fields to change."""
    label: Optional[str] = Field(None, json_schema_extra={"example": "12J"})
    hand_config: Optional[str] = Field(None, json_schema_extra={"example": "Right"})

    model_config = {
        "json_schema_extra": {
            "examples": [
                {"label": "17B", "hand_config": "Left"},
                {"label": "4A"},
            ]
        }
    }


class DeskRead(DeskBase):
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
                    "id": "550e8400-e29b-41d4-a716-446655440000",
                    "label": "12H",
                    "hand_config": "Right",
                    "created_at": "2025-01-15T10:20:30Z",
                    "updated_at": "2025-01-16T12:00:00Z",
                }
            ]
        }
    }
