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


class UUIDv7Cat:
    """UUIDv7 with an embedded category field."""

    def __init__(self, u: Union[str, uuid.UUID]):
        if isinstance(u, str):
            self._uuid = uuid.UUID(u)
        elif isinstance(u, uuid.UUID):
            self._uuid = u
        else:
            raise TypeError(
                "UUIDv7Cat must be initialized with a UUID object or string."
            )

        if self._uuid.version != _UUID_VERSION:
            raise ValueError("Not a v7 UUID")

    @property
    def int(self):
        return self._uuid.int

    @property
    def category(self):
        """Return the embedded type field (0–255)."""
        Category = CategoryProvider.get_categories()
        # The category is stored in the 8 most significant bits of the `rand_a` field.
        # These are bits 68-75 of the UUID.
        type_id = (self.int >> 68) & 0xFF
        if type_id in Category._value2member_map_:
            return Category(type_id)
        else:
            return None

    @property
    def version(self):
        return self._uuid.version

    @property
    def variant(self):
        return self._uuid.variant

    def __repr__(self):
        cat = self.category
        cat_id = (self.int >> 68) & 0xFF
        cat_str = (
            f"cat={cat.name}({cat.value})"
            if cat is not None
            else f"cat=INVALID({cat_id})"
        )
        timestamp_part = (self.int >> 80) & ((1 << 48) - 1)
        return (
            f"UUIDv7Cat('{self._uuid}', ver={self.version}, variant={self.variant}, "
            f"timestamp_part={timestamp_part}, {cat_str})"
        )

    def __str__(self):
        return str(self._uuid)

    def __eq__(self, other):
        return isinstance(other, (UUIDv7Cat, uuid.UUID)) and self.int == other.int

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

        # Manually construct the UUIDv7 to ensure Python version compatibility.
        unix_ts_ms = int(time.time() * 1000)
        ts_field = unix_ts_ms & ((1 << 48) - 1)

        # Generate 74 random bits for rand_a and rand_b
        rand_bytes = os.urandom(10)  # 80 bits is more than enough
        rand_int = int.from_bytes(rand_bytes, "big")
        rand_a = rand_int >> 62 & ((1 << 12) - 1)  # 12 bits for rand_a
        rand_b = rand_int & ((1 << 62) - 1)  # 62 bits for rand_b

        cat_field = cat.value & 0xFF

        # Construct the 128-bit integer
        uuid_int = (
            (ts_field << 80)  # 48-bit timestamp
            | (_UUID_VERSION << 76)
            | (rand_a << 64)
            | (_UUID_VARIANT_RFC4122_BITS << 62)
            | rand_b
        )
        # Clear the 8 bits in rand_a where the category will be stored (bits 68-75)
        cleared_int = uuid_int & ~((0xFF) << 68)

        # Inject the category into the cleared bits
        uuid_int = cleared_int | (cat_field << 68)
        return cls(uuid.UUID(int=uuid_int))

    @staticmethod
    def _basic_validity_check(
        u: Union[str, uuid.UUID, "UUIDv7Cat"],
    ) -> uuid.UUID | None:
        if isinstance(u, str):
            try:
                u = uuid.UUID(u)
            except (ValueError, TypeError):
                return None

        if u.version == _UUID_VERSION and u.variant == uuid.RFC_4122:
            # If it's our own type, extract the inner UUID
            if isinstance(u, UUIDv7Cat):
                return u._uuid
            return u
        return None

    @staticmethod
    def get_category(u: Union[str, uuid.UUID, "UUIDv7Cat"]):
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
            type_id = (u_obj.int >> 68) & 0xFF
            if type_id in Category._value2member_map_:
                return Category(type_id)
        return None

    @staticmethod
    def get_timestamp_sec(u: Union[str, uuid.UUID, "UUIDv7Cat"]) -> str | None:
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
            # The timestamp is now untouched, so we can extract it normally.
            timestamp_part = u_obj.int >> 80
            return time.strftime(
                "%Y-%m-%dT%H:%M:%SZ", time.gmtime(timestamp_part / 1000)
            )
        return None

    @staticmethod
    def is_valid(u: Union[str, uuid.UUID, "UUIDv7Cat"]) -> bool:
        """
        Check if a UUID is a valid UUIDv7Cat.

        Args:
            u: UUID or string

        Returns:
            bool: True if valid, False otherwise.
        """
        return UUIDv7Cat.get_category(u) is not None
