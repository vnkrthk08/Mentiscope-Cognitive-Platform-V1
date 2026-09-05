from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """SQLAlchemy 2.x Declarative Base Class."""

    pass


# Import all ORM models so Base.metadata is fully populated across all subsystems
import app.infrastructure.persistence.models.orm_models  # noqa: F401
import app.infrastructure.identity.orm_models  # noqa: F401
import app.infrastructure.media.orm_models  # noqa: F401
import app.infrastructure.speech.orm_models  # noqa: F401
import app.infrastructure.prompt.orm_models  # noqa: F401
import app.infrastructure.behavior.orm_models  # noqa: F401
import app.infrastructure.construct.orm_models  # noqa: F401
import app.infrastructure.assessment.orm_models  # noqa: F401
import app.infrastructure.research.orm_models  # noqa: F401
import app.infrastructure.analytics.orm_models  # noqa: F401
import app.infrastructure.governance.orm_models  # noqa: F401
import app.infrastructure.actp.orm_models  # noqa: F401
import app.infrastructure.operations.orm_models  # noqa: F401

