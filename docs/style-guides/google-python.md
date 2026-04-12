# Google Python Style Guide

> Source: https://google.github.io/styleguide/pyguide.html

## Language Rules

### Linting & Imports
- Run `pylint` on code using the provided configuration
- Use full package names in imports rather than relative imports
- Avoid `except:` catch-all statements

### Exceptions
- Use built-in exceptions appropriately
- Don't use assertions for validating preconditions -- they may be disabled at runtime
- Minimize code within `try`/`except` blocks and use `finally` for cleanup

### Global State
- Avoid mutable global state
- Internal mutable globals should be prefixed with underscore

### Nested Functions
- Acceptable when closing over local variables
- Avoid nesting merely to hide functions from users

### Comprehensions
- Single `for` clauses are fine; multiple clauses reduce readability

### Generators
- Use `yield` statements and document with "Yields:" in docstrings rather than "Returns:"

### Lambda Functions
- Fine for one-liners; use `operator` module functions instead for basic operations

### Properties
- Permitted when logic is trivial and matches typical attribute expectations; use `@property`

### Type Annotations
- Strongly encouraged
- Type-check at build time using tools like pytype/pyright

## Style Rules

### Line Length
- Maximum 80 characters, with exceptions for URLs and long constants

### Indentation
- Use 4 spaces; never tabs
- Use implicit line joining within parentheses instead of backslashes

### Naming Conventions

| Type | Convention | Example |
|------|-----------|---------|
| Modules/packages | `lower_with_under` | `my_module` |
| Classes | `CapWords` | `MyClass` |
| Functions/methods | `lower_with_under()` | `my_function()` |
| Constants | `CAPS_WITH_UNDER` | `MAX_RETRIES` |
| Instance variables | `lower_with_under` | `self.my_var` |

### Strings
- Use f-strings, `%` operator, or `.format()` for formatting
- Avoid concatenating strings in loops; use `''.join()` instead

### Docstrings
- Use `"""triple quotes"""`
- Include summary line, then sections for Args, Returns, Raises as needed

```python
def fetch_rows(
    table_handle: Table,
    keys: Sequence[bytes | str],
    require_all_keys: bool = False,
) -> Mapping[bytes, tuple[str, ...]]:
    """Fetches rows from a table.

    Args:
        table_handle: An open Table instance.
        keys: A sequence of strings representing row keys.
        require_all_keys: If True only rows with all keys set are returned.

    Returns:
        A dict mapping keys to the corresponding row data.

    Raises:
        BadTableError: An error occurred accessing the table.
    """
```

### Comments
- Explain *why* code exists, not *what* it does
- Start at least 2 spaces from code

### Files & Resources
- Use `with` statements to ensure proper cleanup of files, sockets, and connections

### Main Block
- Check `if __name__ == '__main__':` before executing main code to enable importability
