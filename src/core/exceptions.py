from uuid import UUID


class DomainError(Exception):
    pass


class NotFoundError(DomainError):
    def __init__(self, entity: str, entity_id: int | str | UUID) -> None:
        self.entity = entity
        self.entity_id = entity_id
        super().__init__(f"{entity} with id={entity_id} not found")


class ValidationError(DomainError):
    def __init__(self, field: str, message: str) -> None:
        self.field = field
        super().__init__(f"{field}: {message}")


class AddressNotFoundError(NotFoundError):
    def __init__(self, address_id: UUID) -> None:
        super().__init__("Address", address_id)
