class DomainError(Exception):
    """Base class for domain errors mapped to HTTP responses.

    Subclasses override ``code`` (machine-readable identifier) and may
    override ``status_code`` (HTTP status). Subclasses raised in services
    are translated to HTTP responses by handlers registered in app.main.
    """

    status_code: int = 500
    code: str = "domain_error"

    def __init__(self, message: str = "") -> None:
        super().__init__(message)
        self.message = message or self.code


class EmployeeNotFound(DomainError):
    status_code = 404
    code = "employee_not_found"

    def __init__(self, employee_id: int) -> None:
        super().__init__(f"Employee with id {employee_id} not found")
        self.employee_id = employee_id


class DuplicateEmployeeEmail(DomainError):
    status_code = 409
    code = "duplicate_email"

    def __init__(self, email: str) -> None:
        super().__init__(f"Employee with email {email!r} already exists")
        self.email = email
