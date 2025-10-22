"""
Author: Martin

Date: 2025-09-02

License: Unlicense

Description:
    Used for dependency injection, provides the categories used in the actual implementation
"""

import json
from enum import Enum
from typing import Optional, Type, cast, Dict, Any


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
    def set_categories_from_json(
        cls, json_payload: str, enum_name: str = "DynamicCategory"
    ):
        """
        Load categories from a JSON string and set them.
        The JSON string should contain a dictionary of category names to integer values.
        e.g., '{"CAR": 1, "TRUCK": 2}'
        """
        try:
            categories = json.loads(json_payload)
            # Create an Enum class dynamically from the JSON data
            dynamic_enum_class = Enum(enum_name, categories)
            cls.set_categories(cast(Type[Enum], dynamic_enum_class))
        except (json.JSONDecodeError, TypeError) as e:
            # Catches both bad JSON and invalid dictionary values for an Enum
            raise ValueError(f"Failed to load categories from JSON payload: {e}") from e

    @classmethod
    def get_categories(cls) -> Type[Enum]:
        """Get the current category enum"""
        if cls._category_enum is None:
            # If no enum is configured, return the default without setting it globally.
            from uuidcat.category import Category

            return Category
        return cls._category_enum

    @classmethod
    def reset(cls):
        """Reset to default categories (useful for testing)"""
        cls._category_enum = None
