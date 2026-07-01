"""Backward-compatible imports for legacy ``configMESH`` module name.

This shim keeps existing user code and older tests working while the canonical
module name is ``config_mesh``.
"""

from .config_mesh import *  # noqa: F401,F403
