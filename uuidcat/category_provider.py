"""
Author: Martin

Date: 2025-09-02

License: Unlicense

Description:
    Used for dependency injection, provides the categories used in the actual implementation
"""

from enum import Enum
from typing import Optional, Type


class CategoryProvider:
    """Singleton provider for category configuration"""

    _category_enum: Optional[Type[Enum]] = None

    @classmethod
    def set_categories(cls, category_enum: Type[Enum]):
        """Set the category enum to use"""
        if not issubclass(category_enum, Enum):
            raise TypeError("category_enum must be an Enum class")
        cls._category_enum = category_enum

    @classmethod
    def get_categories(cls) -> Type[Enum]:
        """Get the current category enum"""
        if cls._category_enum is None:
            # Load default
            from uuidcat.category import Category

            cls._category_enum = Category
        return cls._category_enum

    @classmethod
    def reset(cls):
        """Reset to default categories (useful for testing)"""
        cls._category_enum = None
