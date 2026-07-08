"""
Constrictor Framework

A microframework based on Flask for creating modular applications.
"""

from .blueprint_loader import load
from .db import db, migrate

__version__ = "1.0.0"
__all__ = ["load", "db", "migrate"]
