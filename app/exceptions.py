# app/exceptions.py

class ORMError(Exception):
    """Base exception for all MiniORM errors."""
    pass


class ValidationError(ORMError):
    """Raised when a field value fails validation checks."""
    pass


class DoesNotExist(ORMError):
    """
    Raised when a query expects a single record to be returned 
    but finds nothing in the database.
    """
    pass


class MultipleObjectsReturned(ORMError):
    """
    Raised when a query expects only one record but the database 
    returns multiple matching rows.
    """
    pass


class ORMDatabaseError(ORMError):
    """
    Wrapper exception for low-level database operations that fail 
    (e.g., connection drops, bad syntax, constraint violations).
    """
    pass