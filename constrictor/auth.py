"""
Authentication and authorization for Constrictor.

Wraps Flask-Login for session handling and adds two composable, independent
gates for view functions:

- roles_required(*names): simple, code-based - the caller must hold one of
  the named roles (or a role that implies one of them).
- model_access_required(model_name, action): data-based - the caller must
  hold an auth_model_access grant for `action` on `model_name`. Grants live
  in the database, seeded from each module's access.csv, and can be changed
  at runtime without a redeploy.
"""

import csv
from functools import wraps
from pathlib import Path

from flask import abort
from flask_login import LoginManager, current_user, login_required, login_user, logout_user

from .auth_models import ModelAccess, Role, User
from .db import db

login_manager = LoginManager()

__all__ = [
    "login_manager",
    "login_required",
    "current_user",
    "login_user",
    "logout_user",
    "roles_required",
    "model_access_required",
    "seed_access_from_csv",
]


@login_manager.user_loader
def _load_user(user_id):
    return db.session.get(User, int(user_id))


def roles_required(*role_names):
    """Require an authenticated user holding at least one of role_names
    (directly, or via a role that implies one of them)."""
    def decorator(view):
        @wraps(view)
        def wrapped(*args, **kwargs):
            if not any(current_user.has_role(name) for name in role_names):
                abort(403)
            return view(*args, **kwargs)
        return login_required(wrapped)
    return decorator


def model_access_required(model_name, action):
    """Require an authenticated user with an auth_model_access grant for
    `action` (read/create/update/delete) on `model_name`."""
    def decorator(view):
        @wraps(view)
        def wrapped(*args, **kwargs):
            if not current_user.can(model_name, action):
                abort(403)
            return view(*args, **kwargs)
        return login_required(wrapped)
    return decorator


_TRUE_VALUES = {"1", "true", "yes", "y"}


def _get_or_create_role(name):
    role = Role.query.filter_by(name=name).first()
    if role is None:
        role = Role(name=name)
        db.session.add(role)
        db.session.flush()
    return role


def seed_access_from_csv(csv_path: Path) -> int:
    """
    Seed auth_role/auth_model_access from a module's access.csv (columns:
    model, role, can_read, can_create, can_update, can_delete - role blank
    means "any authenticated user").

    Insert-if-missing only: an existing (role, model) grant is never
    overwritten, so a redeploy can't silently revert a grant that was
    changed at runtime (mirrors Odoo's noupdate semantics for security data).

    Returns the number of grants inserted.
    """
    inserted = 0
    with open(csv_path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            model_name = (row.get("model") or "").strip()
            if not model_name:
                continue

            role_name = (row.get("role") or "").strip()
            role = _get_or_create_role(role_name) if role_name else None
            role_id = role.id if role else None

            existing = ModelAccess.query.filter_by(role_id=role_id, model_name=model_name).first()
            if existing is not None:
                continue

            def flag(key):
                return (row.get(key) or "").strip().lower() in _TRUE_VALUES

            db.session.add(ModelAccess(
                role_id=role_id,
                model_name=model_name,
                can_read=flag("can_read"),
                can_create=flag("can_create"),
                can_update=flag("can_update"),
                can_delete=flag("can_delete"),
            ))
            inserted += 1

    db.session.commit()
    return inserted
