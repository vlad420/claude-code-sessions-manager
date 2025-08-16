from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum, unique


@unique
class SessionStatus(StrEnum):
    ACTIVE = "active"
    EXPIRED = "expired"


@dataclass(frozen=True)
class Session:
    created_at: datetime
    expires_at: datetime
    status: SessionStatus

    @classmethod
    def create_active(cls, created_at: datetime, expires_at: datetime) -> "Session":
        return cls(
            created_at=created_at,
            expires_at=expires_at,
            status=SessionStatus.ACTIVE
        )

    @classmethod
    def from_data(cls, created_at: datetime, expires_at: datetime) -> "Session":
        status = SessionStatus.ACTIVE if expires_at > datetime.now() else SessionStatus.EXPIRED
        return cls(
            created_at=created_at,
            expires_at=expires_at,
            status=status
        )

    @property
    def is_active(self) -> bool:
        return self.status == SessionStatus.ACTIVE and self.expires_at > datetime.now()

    @property
    def is_expired(self) -> bool:
        return not self.is_active