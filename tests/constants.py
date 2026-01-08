class ValidationStatusValues:
    PENDING = "pending"
    VERIFIED = "verified"
    WARNING = "warning"
    ERROR = "error"


class HealthStatus:
    OK = "ok"


class AddressData:
    NAME_DEFAULT = "John Doe"
    COMPANY_DEFAULT = "Acme Inc"
    PHONE_DEFAULT = "+1-555-123-4567"
    ADDRESS_LINE1_DEFAULT = "123 Main Street"
    ADDRESS_LINE1_PO_BOX = "PO Box 123"
    ADDRESS_LINE2_DEFAULT = "Suite 100"
    CITY_DEFAULT = "Austin"
    CITY_UPDATED = "New York"
    STATE_DEFAULT = "TX"
    POSTAL_CODE_DEFAULT = "78701"
    POSTAL_CODE_INVALID = "12"
    COUNTRY_CODE_US = "US"
    COUNTRY_CODE_INVALID = "X"


class TestIds:
    FAKE_UUID = "00000000-0000-0000-0000-000000000000"


class ValidationMessages:
    INVALID_POSTAL_CODE = "Invalid or missing postal code"
    INVALID_COUNTRY_CODE = "Country code must be 2 characters"
    ADDRESS_LINE1_REQUIRED = "Address line 1 is required"
    CITY_REQUIRED = "City is required"
    PO_BOX_WARNING = "Address appears to be a PO Box"


class StatusCodes:
    OK = 200
    CREATED = 201
    NO_CONTENT = 204
    BAD_REQUEST = 400
    NOT_FOUND = 404
    UNPROCESSABLE = 422


class TaskNames:
    VALIDATE_ADDRESS = "validate_address_task"
