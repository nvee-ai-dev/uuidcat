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
import json
from enum import Enum

import pytest

from uuidcat.category_provider import CategoryProvider
from uuidcat.uuidcat import UUIDv7Cat


class TestCategory(Enum):
    """Custom categories for testing."""

    RED = 10
    GREEN = 20
    BLUE = 30


@pytest.fixture
def setup_teardown():
    """Fixture to ensure a clean state for each test."""
    # Setup: configure categories for tests
    CategoryProvider.set_categories(TestCategory)
    yield
    # Teardown: reset to default
    CategoryProvider.reset()


@pytest.mark.usefixtures("setup_teardown")
def test_new_uuid_creation():
    """Test creation of a new UUIDv7Cat."""
    cat = TestCategory.GREEN
    uuid_obj = UUIDv7Cat.new(cat)

    assert isinstance(uuid_obj, UUIDv7Cat)
    assert uuid_obj.version == 7
    assert uuid_obj.variant == uuid.RFC_4122
    assert uuid_obj.category == cat


@pytest.mark.usefixtures("setup_teardown")
def test_new_uuid_with_invalid_category_value():
    """Test that creating a UUID with an out-of-range category value fails."""

    class BadCategory(Enum):
        TOO_BIG = 256

    # Temporarily set the categories to the one that will cause the error
    CategoryProvider.set_categories(BadCategory)

    with pytest.raises(ValueError, match="Category value must be in range 0..255"):
        # This call will now use BadCategory and fail as expected
        UUIDv7Cat.new(BadCategory.TOO_BIG)


@pytest.mark.usefixtures("setup_teardown")
def test_category_property():
    """Test the category property on a UUIDv7Cat instance."""
    uuid_obj = UUIDv7Cat.new(TestCategory.RED)
    assert uuid_obj.category == TestCategory.RED


@pytest.mark.usefixtures("setup_teardown")
def test_category_property_with_unknown_id():
    """Test the category property when the category ID is not in the enum."""
    # Manually construct a UUID with a category ID (e.g., 99) not in TestCategory
    base_uuid_int = UUIDv7Cat.new(TestCategory.RED).int
    # Clear the category bits (68-75) and set them to 99
    uuid_int = (base_uuid_int & ~((0xFF) << 68)) | (99 << 68)
    uuid_obj = UUIDv7Cat(uuid.UUID(int=uuid_int))

    assert uuid_obj.category is None


@pytest.mark.usefixtures("setup_teardown")
def test_str_representation():
    """Test the string representation of UUIDv7Cat."""
    uuid_obj = UUIDv7Cat.new(TestCategory.BLUE)
    # Should be a standard UUID hex string
    assert len(str(uuid_obj)) == 36
    # Check that it can be parsed back into a standard UUID
    assert uuid.UUID(str(uuid_obj)) == uuid_obj


@pytest.mark.usefixtures("setup_teardown")
def test_repr_representation():
    """Test the repr representation of UUIDv7Cat."""
    uuid_obj = UUIDv7Cat.new(TestCategory.BLUE)
    repr_str = repr(uuid_obj)

    assert "UUIDv7Cat" in repr_str
    assert "ver=7" in repr_str
    assert "variant=specified in RFC 4122" in repr_str
    assert "cat=BLUE(30)" in repr_str


@pytest.mark.usefixtures("setup_teardown")
def test_repr_with_invalid_category():
    """Test the repr representation with an invalid category ID."""
    base_uuid_int = UUIDv7Cat.new(TestCategory.RED).int
    # Clear the category bits (68-75) and set them to 150
    uuid_int = (base_uuid_int & ~((0xFF) << 68)) | (150 << 68)
    uuid_obj = UUIDv7Cat(uuid.UUID(int=uuid_int))  # Use the correct constructor
    repr_str = repr(uuid_obj)

    assert "cat=INVALID(150)" in repr_str


@pytest.mark.usefixtures("setup_teardown")
def test_get_category():
    """Test the static get_category method."""
    uuid_obj = UUIDv7Cat.new(TestCategory.GREEN)

    # Test with UUID object
    assert UUIDv7Cat.get_category(uuid_obj) == TestCategory.GREEN
    # Test with string representation
    assert UUIDv7Cat.get_category(str(uuid_obj)) == TestCategory.GREEN


@pytest.mark.usefixtures("setup_teardown")
def test_get_category_invalid_inputs():
    """Test get_category with various invalid inputs."""
    # Invalid UUID string
    assert UUIDv7Cat.get_category("not-a-uuid") is None
    # UUIDv4
    assert UUIDv7Cat.get_category(uuid.uuid4()) is None
    # UUID with a category ID not in the enum
    base_uuid_int = UUIDv7Cat.new(TestCategory.RED).int
    # Clear the category bits (68-75) and set them to 99
    uuid_int = (base_uuid_int & ~((0xFF) << 68)) | (99 << 68)
    uuid_obj = UUIDv7Cat(uuid.UUID(int=uuid_int))
    assert UUIDv7Cat.get_category(uuid_obj) is None


@pytest.mark.usefixtures("setup_teardown")
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
    assert start_time - 2 <= ts_from_uuid <= end_time + 2  # Allow a 2-second window


@pytest.mark.usefixtures("setup_teardown")
def test_get_timestamp_sec_invalid_input():
    """Test get_timestamp_sec with an invalid UUID."""
    assert UUIDv7Cat.get_timestamp_sec(uuid.uuid4()) is None
    assert UUIDv7Cat.get_timestamp_sec("not-a-uuid") is None


@pytest.mark.usefixtures("setup_teardown")
def test_is_valid():
    """Test the static is_valid method."""
    valid_uuid = UUIDv7Cat.new(TestCategory.BLUE)
    assert UUIDv7Cat.is_valid(valid_uuid) is True
    assert UUIDv7Cat.is_valid(str(valid_uuid)) is True


@pytest.mark.usefixtures("setup_teardown")
def test_is_valid_false_cases():
    """Test is_valid for cases where it should return False."""
    # UUIDv4
    assert UUIDv7Cat.is_valid(uuid.uuid4()) is False
    # Invalid string
    assert UUIDv7Cat.is_valid("not-a-uuid") is False
    # UUIDv7Cat with a category ID not in the current enum
    base_uuid_int = UUIDv7Cat.new(TestCategory.RED).int
    # Clear the category bits (68-75) and set them to 99
    uuid_int = (base_uuid_int & ~((0xFF) << 68)) | (99 << 68)
    invalid_cat_uuid = UUIDv7Cat(uuid.UUID(int=uuid_int))
    assert UUIDv7Cat.is_valid(invalid_cat_uuid) is False


@pytest.mark.usefixtures("setup_teardown")
def test_set_categories_from_json():
    """Test loading categories from a JSON string."""
    json_categories = {"ALPHA": 100, "BETA": 101, "GAMMA": 102}
    json_payload = json.dumps(json_categories)

    CategoryProvider.set_categories_from_json(json_payload)
    DynamicCategory = CategoryProvider.get_categories()

    # Verify the enum was created correctly
    assert issubclass(DynamicCategory, Enum)
    assert getattr(DynamicCategory, "ALPHA").value == 100
    assert getattr(DynamicCategory, "BETA").name == "BETA"
    assert len(DynamicCategory) == 3

    # Verify integration with UUIDv7Cat
    uuid_obj = UUIDv7Cat.new(getattr(DynamicCategory, "GAMMA"))
    assert uuid_obj.category == getattr(DynamicCategory, "GAMMA")
    assert UUIDv7Cat.is_valid(uuid_obj)


@pytest.mark.usefixtures("setup_teardown")
def test_set_categories_from_invalid_json():
    """Test that loading from a malformed JSON string raises an error."""
    # Invalid JSON due to a trailing comma
    invalid_json_payload = '{"A": 1, "B": 2,}'

    with pytest.raises(ValueError) as excinfo:
        CategoryProvider.set_categories_from_json(invalid_json_payload)

    # Check that the ValueError was caused by a JSONDecodeError
    assert isinstance(excinfo.value, ValueError)
    assert isinstance(excinfo.value.__cause__, json.JSONDecodeError)


@pytest.mark.usefixtures("setup_teardown")
def test_reset_causes_default_fallback():
    """Test that after a reset, get_categories falls back to the default."""
    CategoryProvider.reset()  # Reset to ensure no categories are set

    from uuidcat.category import Category as DefaultCategory

    # get_categories should now load the default
    assert CategoryProvider.get_categories() == DefaultCategory

    # Verify that a UUID can be created with the default enum
    uuid_obj = UUIDv7Cat.new(DefaultCategory.TYPE_A)
    assert uuid_obj.category == DefaultCategory.TYPE_A
    assert UUIDv7Cat.is_valid(uuid_obj)


@pytest.mark.usefixtures("setup_teardown")
def test_is_valid_after_category_change():
    """Test that is_valid reflects the currently configured categories."""
    # 1. Create a UUID with the initial TestCategory
    uuid_with_test_category = UUIDv7Cat.new(TestCategory.RED)
    assert UUIDv7Cat.is_valid(uuid_with_test_category) is True

    # 2. Change the provider to use the default categories
    from uuidcat.category import Category as DefaultCategory

    CategoryProvider.set_categories(DefaultCategory)

    # 3. The original UUID should now be considered invalid
    assert UUIDv7Cat.is_valid(uuid_with_test_category) is False
