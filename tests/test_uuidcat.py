"""
Author: Martin

Date: 2025-09-02

License: Unlicense

Description:
    Unit tests for the UUIDv7Cat class.
"""

import calendar
import time
import uuid
from enum import Enum

import pytest

from uuidcat.category_provider import CategoryProvider
from uuidcat.uuidcat import UUIDv7Cat


class TestCategory(Enum):
    """Custom categories for testing."""

    RED = 10
    GREEN = 20
    BLUE = 30


@pytest.fixture(autouse=True)
def setup_teardown():
    """Fixture to ensure a clean state for each test."""
    # Setup: configure categories for tests
    CategoryProvider.set_categories(TestCategory)
    yield
    # Teardown: reset to default
    CategoryProvider.reset()


def test_new_uuid_creation():
    """Test creation of a new UUIDv7Cat."""
    cat = TestCategory.GREEN
    uuid_obj = UUIDv7Cat.new(cat)

    assert isinstance(uuid_obj, UUIDv7Cat)
    assert uuid_obj.version == 7
    assert uuid_obj.variant == uuid.RFC_4122
    assert uuid_obj.category == cat


def test_new_uuid_with_invalid_category_value():
    """Test that creating a UUID with an out-of-range category value fails."""

    class BadCategory(Enum):
        TOO_BIG = 256

    # Temporarily set the categories to the one that will cause the error
    CategoryProvider.set_categories(BadCategory)

    with pytest.raises(ValueError, match="Category value must be in range 0..255"):
        # This call will now use BadCategory and fail as expected
        UUIDv7Cat.new(BadCategory.TOO_BIG)


def test_category_property():
    """Test the category property on a UUIDv7Cat instance."""
    uuid_obj = UUIDv7Cat.new(TestCategory.RED)
    assert uuid_obj.category == TestCategory.RED


def test_category_property_with_unknown_id():
    """Test the category property when the category ID is not in the enum."""
    # Manually construct a UUID with a category ID (e.g., 99) not in TestCategory
    base_uuid = UUIDv7Cat.new(TestCategory.RED)
    uuid_int = (99 << 120) | (base_uuid.int & ((1 << 120) - 1))
    uuid_obj = UUIDv7Cat(int=uuid_int)  # Use the correct constructor

    assert uuid_obj.category is None


def test_str_representation():
    """Test the string representation of UUIDv7Cat."""
    uuid_obj = UUIDv7Cat.new(TestCategory.BLUE)
    # Should be a standard UUID hex string
    assert str(uuid_obj) == uuid_obj.hex
    # Check that it can be parsed back into a standard UUID
    assert uuid.UUID(str(uuid_obj)) == uuid_obj


def test_repr_representation():
    """Test the repr representation of UUIDv7Cat."""
    uuid_obj = UUIDv7Cat.new(TestCategory.BLUE)
    repr_str = repr(uuid_obj)

    assert "UUIDv7Cat" in repr_str
    assert "ver=7" in repr_str
    assert f"variant={uuid.RFC_4122}" in repr_str
    assert "cat=BLUE(30)" in repr_str


def test_repr_with_invalid_category():
    """Test the repr representation with an invalid category ID."""
    base_uuid = UUIDv7Cat.new(TestCategory.RED)
    uuid_int = (150 << 120) | (base_uuid.int & ((1 << 120) - 1))
    uuid_obj = UUIDv7Cat(int=uuid_int)  # Use the correct constructor
    repr_str = repr(uuid_obj)

    assert "cat=INVALID(150)" in repr_str


def test_get_category():
    """Test the static get_category method."""
    uuid_obj = UUIDv7Cat.new(TestCategory.GREEN)

    # Test with UUID object
    assert UUIDv7Cat.get_category(uuid_obj) == TestCategory.GREEN
    # Test with string representation
    assert UUIDv7Cat.get_category(str(uuid_obj)) == TestCategory.GREEN


def test_get_category_invalid_inputs():
    """Test get_category with various invalid inputs."""
    # Invalid UUID string
    assert UUIDv7Cat.get_category("not-a-uuid") is None
    # UUIDv4
    assert UUIDv7Cat.get_category(uuid.uuid4()) is None
    # UUID with a category ID not in the enum
    uuid_int = (99 << 120) | (UUIDv7Cat.new(TestCategory.RED).int & ((1 << 120) - 1))
    uuid_obj = UUIDv7Cat(int=uuid_int)
    assert UUIDv7Cat.get_category(uuid_obj) is None


def test_get_timestamp_sec():
    """Test the static get_timestamp_sec method."""
    start_time = time.time()
    uuid_obj = UUIDv7Cat.new(TestCategory.RED)
    end_time = time.time()

    ts_str = UUIDv7Cat.get_timestamp_sec(uuid_obj)
    assert isinstance(ts_str, str)
    assert ts_str.endswith("Z")

    # Parse the timestamp and check if it's within the creation window
    # Use calendar.timegm to correctly interpret the UTC 'Z' timestamp
    utc_struct_time = time.strptime(ts_str, "%Y-%m-%dT%H:%M:%SZ")
    ts_from_uuid = calendar.timegm(utc_struct_time)
    # Allow a small buffer for execution time
    assert start_time - 1 <= ts_from_uuid <= end_time + 1


def test_get_timestamp_sec_invalid_input():
    """Test get_timestamp_sec with an invalid UUID."""
    assert UUIDv7Cat.get_timestamp_sec(uuid.uuid4()) is None
    assert UUIDv7Cat.get_timestamp_sec("not-a-uuid") is None


def test_is_valid():
    """Test the static is_valid method."""
    valid_uuid = UUIDv7Cat.new(TestCategory.BLUE)
    assert UUIDv7Cat.is_valid(valid_uuid) is True
    assert UUIDv7Cat.is_valid(str(valid_uuid)) is True


def test_is_valid_false_cases():
    """Test is_valid for cases where it should return False."""
    # UUIDv4
    assert UUIDv7Cat.is_valid(uuid.uuid4()) is False
    # Invalid string
    assert UUIDv7Cat.is_valid("not-a-uuid") is False
    # UUIDv7Cat with a category ID not in the current enum
    uuid_int = (99 << 120) | (UUIDv7Cat.new(TestCategory.RED).int & ((1 << 120) - 1))
    invalid_cat_uuid = UUIDv7Cat(int=uuid_int)
    assert UUIDv7Cat.is_valid(invalid_cat_uuid) is False


def test_default_categories_fallback():
    """Test that the default categories are used if none are set."""
    CategoryProvider.reset()  # Reset to ensure no categories are set

    from uuidcat.category import Category as DefaultCategory

    # get_categories should now load the default
    assert CategoryProvider.get_categories() == DefaultCategory

    # Create a UUID using the default category enum
    uuid_obj = UUIDv7Cat.new(DefaultCategory.TYPE_A)
    assert uuid_obj.category == DefaultCategory.TYPE_A
    assert UUIDv7Cat.is_valid(uuid_obj)

    # Now, check that a UUID created with the test enum is considered invalid
    # because the provider is now configured with the default enum.
    CategoryProvider.set_categories(TestCategory)
    other_uuid = UUIDv7Cat.new(TestCategory.RED)

    CategoryProvider.reset()  # Fallback to default again
    assert UUIDv7Cat.is_valid(other_uuid) is False
