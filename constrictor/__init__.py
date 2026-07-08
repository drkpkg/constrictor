"""
Constrictor Framework

A microframework based on Flask for creating modular applications.
"""

from .blueprint_loader import load
from .db import db, migrate
from .auth_models import User, Role, ModelAccess
from .auth import (
    login_manager,
    login_required,
    current_user,
    login_user,
    logout_user,
    roles_required,
    model_access_required,
)

__version__ = "1.0.0"
__all__ = [
    "load",
    "db",
    "migrate",
    "User",
    "Role",
    "ModelAccess",
    "login_manager",
    "login_required",
    "current_user",
    "login_user",
    "logout_user",
    "roles_required",
    "model_access_required",
]
