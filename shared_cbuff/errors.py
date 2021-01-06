class CBuffException(Exception):
    """Base exception for all exceptions raised by the library."""

    pass


class WriteOperationsForbidden(Exception):
    """Exception raised when a write operation is attempted but is not permitted."""

    pass


class ReadOperationsForbidden(Exception):
    """Exception raised when a read operation is attempted but is not permitted."""

    pass
