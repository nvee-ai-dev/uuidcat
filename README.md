# Categorised UUIDv7
Takes a standard UUID v7, and co-opts some bits to inject a category. This can be used to determine the cateegory of object the UUID has been assigned to

## Example usage
See the `/examples' directory for a simple usecase. 
- create a wrapper file for the UUID class, e.g. `uuid_wrapper.py`
- in the wrapper file, define your own custom categories
- configure the CategoryProvider with the categories
- re-export the UUIDv7Cat class and your custom categories class

e.g.,
```python
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
```

Then in your code, import the UUIDv7 and the custom categories class from the wrapper file.
```python
from uuid_wrapper import UUIDv7Cat, ExampleCategory
```