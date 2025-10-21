"""
Author: Martin

Date: 2025-09-02

License: Unlicense

Description:
    Usage of the simple wrapper file.
"""

import sys

# Import from your wrapper - categories already configured
from uuid_wrapper import UUIDv7Cat, ExampleCategory


def main() -> int:
    # Use normally
    uuid_obj = UUIDv7Cat.new(ExampleCategory.TRUCK)
    print(uuid_obj)

    # Static methods work as expected
    cat = UUIDv7Cat.get_category(uuid_obj)
    print(cat)

    timestamp = UUIDv7Cat.get_timestamp_sec(uuid_obj)
    print(timestamp)
    return 0


if __name__ == "__main__":
    sys.exit(main())
