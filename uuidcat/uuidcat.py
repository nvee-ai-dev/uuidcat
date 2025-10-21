"""
Author: Martin

Date: 2025-09-02

License: Unlicense

Description:
    Custom UUIDv7 variant with an 8-bit category field.
    - Preserves RFC 4122 version/variant compliance
    - First byte encodes "category"
    - Remaining layout matches UUIDv7 as closely as possible
"""

import os
import time
import uuid
from typing import Union
from uuidcat.category_provider import CategoryProvider

_UUID_VERSION = 7
_UUID_VARIANT_RFC4122_BITS = 0b10


class UUIDv7Cat(uuid.UUID):
    """UUIDv7 with an embedded category field."""

    @property
    def category(self):
        """Return the embedded type field (0–255)."""
        Category = CategoryProvider.get_categories()
        type_id = (self.int >> 120) & 0xFF
        if type_id in Category._value2member_map_:
            return Category(type_id)
        else:
            return None

    def __repr__(self):
        cat = self.category
        cat_str = (
            f"cat={cat.name}({cat.value})"
            if cat
            else f"cat=INVALID({(self.int >> 120) & 0xFF})"
        )
        timestamp_part = (self.int >> 80) & ((1 << 40) - 1)
        return (
            f"UUIDv7Cat(ver={self.version}, variant={self.variant}, "
            f"timestamp_part={timestamp_part}, {cat_str})"
        )

    def __str__(self):
        return self.hex

    @classmethod
    def new(cls, cat) -> "UUIDv7Cat":
        """
        Create a new UUIDv7Cat instance with a given category.

        Args:
            cat: category/type identifier (enum member).

        Returns:
            UUIDv7Cat: UUID object with type embedded.
        """
        if not (0 <= cat.value <= 255):
            raise ValueError("Category value must be in range 0..255")

        unix_ts_ms = int(time.time() * 1000)
        rand_bytes = os.urandom(10)

        cat_field = cat.value & 0xFF
        ts_field = unix_ts_ms & ((1 << 48) - 1)

        rand_int = int.from_bytes(rand_bytes, "big")
        rand_a = rand_int >> (80 - 12) & ((1 << 12) - 1)
        rand_b = rand_int & ((1 << 62) - 1)

        uuid_int = (
            (cat_field << 120)
            | (ts_field << 72)
            | (_UUID_VERSION << 76)
            | (rand_a << 64)
            | (_UUID_VARIANT_RFC4122_BITS << 62)
            | rand_b
        )

        return cls(int=uuid_int)

    @staticmethod
    def _basic_validity_check(u: Union[str, uuid.UUID]) -> uuid.UUID | None:
        if isinstance(u, UUIDv7Cat):
            # If it's already our type, we know it's valid.
            return u

        if isinstance(u, str):
            try:
                u = uuid.UUID(u)
            except ValueError:
                return None

        if u.version == _UUID_VERSION and u.variant == uuid.RFC_4122:
            return u

        return None

    @staticmethod
    def get_category(u: Union[str, uuid.UUID]):
        """
        Extract the category field from a UUID.

        Args:
            u: UUID or string

        Returns:
            Category enum member or None if invalid.
        """
        Category = CategoryProvider.get_categories()
        u_obj = UUIDv7Cat._basic_validity_check(u)
        if u_obj:
            type_id = (u_obj.int >> 120) & 0xFF
            if type_id in Category._value2member_map_:
                return Category(type_id)
        return None

    @staticmethod
    def get_timestamp_sec(u: Union[str, uuid.UUID]) -> str | None:
        """
        Extract the timestamp field from a UUID, converts it to a string in standard
        ISO 8601 date time format, down to seconds granularity

         Args:
            u: UUID or string

        Returns:
            str: string of the timestamp at seconds granularity
            None: If invalid
        """
        u_obj = UUIDv7Cat._basic_validity_check(u)
        if u_obj:
            timestamp_part = (u_obj.int >> 72) & ((1 << 48) - 1)
            return time.strftime(
                "%Y-%m-%dT%H:%M:%SZ", time.gmtime(timestamp_part / 1000)
            )
        return None

    @staticmethod
    def is_valid(u: Union[str, uuid.UUID]) -> bool:
        """
        Check if a UUID is a valid UUIDv7Cat.

        Args:
            u: UUID or string

        Returns:
            bool: True if valid, False otherwise.
        """
        return UUIDv7Cat.get_category(u) is not None
