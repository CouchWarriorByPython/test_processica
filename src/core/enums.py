from enum import Enum


class ValidationStatus(str, Enum):
    PENDING = "pending"
    VERIFIED = "verified"
    UNVERIFIED = "unverified"
    WARNING = "warning"
    ERROR = "error"

    def is_final(self) -> bool:
        return self != ValidationStatus.PENDING
