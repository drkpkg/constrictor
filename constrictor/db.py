"""
Shared database objects for Constrictor modules.

Every module's models.py imports `db` from here and defines its models as
`db.Model` subclasses, so all modules register their tables onto the same
SQLAlchemy metadata even though each module owns its own models.py file.
"""

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()
