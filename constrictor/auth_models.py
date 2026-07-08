"""
Built-in identity and access-control models for Constrictor.

These live at the framework level (imported directly by constrictor/__init__.py,
not inside any generated module) so they're part of db.metadata - and therefore
part of the very first migration - before any user module is even walked.
Table names are prefixed `auth_` so they can't collide with a module named
`role` or `access` (the same convention Django uses for its own auth_user/
auth_group tables).
"""

from datetime import datetime

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from .db import db

auth_user_role = db.Table(
    "auth_user_role",
    db.Column("user_id", db.Integer, db.ForeignKey("auth_user.id"), primary_key=True),
    db.Column("role_id", db.Integer, db.ForeignKey("auth_role.id"), primary_key=True),
)


class Role(db.Model):
    """A named role. May imply another role (e.g. "editor" implies "viewer")."""

    __tablename__ = "auth_role"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    implies_role_id = db.Column(db.Integer, db.ForeignKey("auth_role.id"), nullable=True)

    implies = db.relationship("Role", remote_side=[id])

    def __repr__(self):
        return f"<Role {self.name!r}>"


class User(db.Model, UserMixin):
    """Account identity and credentials. Flask-Login's current_user."""

    __tablename__ = "auth_user"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    roles = db.relationship("Role", secondary=auth_user_role, backref="users")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def _all_roles(self):
        """Directly-held roles plus every role they (transitively) imply."""
        seen = {}
        for role in self.roles:
            current = role
            while current is not None and current.id not in seen:
                seen[current.id] = current
                current = current.implies
        return list(seen.values())

    def role_names(self):
        """Every role this user holds, directly or via implication."""
        return {role.name for role in self._all_roles()}

    def has_role(self, name):
        return name in self.role_names()

    def can(self, model_name, action):
        """Check auth_model_access for whether this user may perform `action`
        (one of read/create/update/delete) on `model_name`."""
        column = {
            "read": ModelAccess.can_read,
            "create": ModelAccess.can_create,
            "update": ModelAccess.can_update,
            "delete": ModelAccess.can_delete,
        }[action]

        role_ids = [role.id for role in self._all_roles()]
        query = ModelAccess.query.filter(ModelAccess.model_name == model_name, column.is_(True))
        if role_ids:
            query = query.filter(db.or_(ModelAccess.role_id.is_(None), ModelAccess.role_id.in_(role_ids)))
        else:
            query = query.filter(ModelAccess.role_id.is_(None))
        return db.session.query(query.exists()).scalar()

    def __repr__(self):
        return f"<User {self.email!r}>"


class ModelAccess(db.Model):
    """A per-role CRUD grant on a model, referenced by name (not a DB foreign
    key - Constrictor's modules are a closed set resolved at startup against
    db.metadata.tables, so there's no need for a persisted model registry the
    way Odoo's ir.model has). A null role_id means "any authenticated user."
    """

    __tablename__ = "auth_model_access"

    id = db.Column(db.Integer, primary_key=True)
    role_id = db.Column(db.Integer, db.ForeignKey("auth_role.id"), nullable=True)
    model_name = db.Column(db.String(255), nullable=False)
    can_read = db.Column(db.Boolean, default=False, nullable=False)
    can_create = db.Column(db.Boolean, default=False, nullable=False)
    can_update = db.Column(db.Boolean, default=False, nullable=False)
    can_delete = db.Column(db.Boolean, default=False, nullable=False)

    role = db.relationship("Role")

    def __repr__(self):
        return f"<ModelAccess {self.model_name!r} role={self.role_id!r}>"
