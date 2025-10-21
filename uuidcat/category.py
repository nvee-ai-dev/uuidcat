"""
uuidcat.py

Author: Martin

Date: 2025-09-02

License: Unlicense

Description:
    This file serves as:

    1. Fallback - If parent project doesn't configure custom categories, these defaults are used

    2. Example - Shows users how to structure their own categories

    3. Testing - Allows the submodule to have its own tests without external dependencies
"""

from enum import Enum


class Category(Enum):
    """Default categories for UUIDv7Cat"""

    UNKNOWN = 0
    TYPE_A = 1
    TYPE_B = 2
    TYPE_C = 3
