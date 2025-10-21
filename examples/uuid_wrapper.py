"""
Author: Martin

Date: 2025-09-02

License: Unlicense

Description:
    An example of how to wrap the categorised UUID class, specifically to enable the category calls.
"""

import sys
from uuidcat.category_provider import CategoryProvider
from uuidcat.uuidcat import UUIDv7Cat

from enum import Enum


class ExampleCategory(Enum):
    CAR = 1
    TRUCK = 2
    BUS = 3


# Configure categories once at module import
CategoryProvider.set_categories(ExampleCategory)

# Re-export for convenience
__all__ = ["UUIDv7Cat", "ExampleCategory"]
