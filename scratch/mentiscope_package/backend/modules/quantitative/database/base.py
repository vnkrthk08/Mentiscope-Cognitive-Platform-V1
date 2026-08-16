"""
==========================================================
SQLAlchemy Declarative Base
==========================================================
"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """
    Base class for every ORM model.

    All database models inherit from this class.
    """
    pass