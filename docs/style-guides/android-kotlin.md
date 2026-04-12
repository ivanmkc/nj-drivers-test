# Android Kotlin Style Guide

> Source: https://developer.android.com/kotlin/style-guide

## Source Files

- UTF-8 encoding, no tab characters
- Single top-level class: filename matches class name + `.kt`
- Multiple declarations: descriptive PascalCase name + `.kt`

## File Structure

Order: Copyright/License, File-level annotations, Package, Imports, Top-level declarations. Each section separated by one blank line.

### Imports
- Grouped together and ASCII sorted
- No wildcard imports
- Not subject to column limit

## Formatting

### Column Limit: 100 characters

### Braces (Egyptian/K&R style)
- No line break before opening brace
- Line break after opening brace
- Line break before closing brace

Single-line omission allowed for `when` branches and simple `if` with no `else`:

```kotlin
if (string.isEmpty()) return

val result = if (string.isEmpty()) DEFAULT_VALUE else string

when (value) {
    0 -> return
}
```

### Indentation: 4 spaces

### One Statement Per Line
- Semicolons not used

### Line Wrapping
- Break after operators and infix function names
- Break after commas
- Break before dot separators (`.`, `?.`)
- Each parameter on own line with +4 indent

```kotlin
fun <T> Iterable<T>.joinToString(
    separator: CharSequence = ", ",
    prefix: CharSequence = "",
    postfix: CharSequence = ""
): String {
    // ...
}
```

### Whitespace
- Space between control keywords and `(`: `if (condition)`
- Space around binary operators: `val two = 1 + 1`
- Space around lambda arrow: `{ value -> value.toString() }`
- No space around `::`, `.`, `..`

### Enum Classes
```kotlin
enum class Answer { YES, NO, MAYBE }

enum class Answer {
    YES,
    NO,
    MAYBE {
        override fun toString() = """..."""
    }
}
```

### Annotations
- Parameterized annotations on own line before declaration
- Single non-parameterized annotations may share line

```kotlin
@JvmField @Volatile
var disposable: Disposable? = null

@Test fun selectAll() { }
```

## Naming

### Package Names
- All lowercase, no underscores: `com.example.deepspace`

### Type Names
- PascalCase, typically nouns: `MyClass`, `MyClassTest`

### Function Names
- camelCase, typically verbs: `sendMessage()`, `stop()`
- Underscores in test names: `pop_emptyStack()`
- `@Composable` returning Unit: PascalCase as nouns: `NameTag(name: String)`

### Constant Names
- `UPPER_SNAKE_CASE` for deeply immutable `val` properties
- Use `const` modifier for scalar constants
- Only in `object` or top-level declarations

```kotlin
const val NUMBER = 5
val NAMES = listOf("Alice", "Bob")
```

### Non-constant Names
- camelCase: `val variable = "var"`

### Backing Properties
- Prefix with underscore: `private var _table: Map<String, Int>? = null`

### Camel Case Rules

| Prose Form | Correct | Incorrect |
|---|---|---|
| "XML Http Request" | `XmlHttpRequest` | `XMLHTTPRequest` |
| "new customer ID" | `newCustomerId` | `newCustomerID` |
| "supports IPv6 on iOS" | `supportsIpv6OnIos` | `supportsIPv6OnIOS` |

## Documentation

- Use KDoc (`/** */`) for public APIs
- Single-line allowed when entire block fits: `/** An especially short bit of KDoc. */`
- Summary fragment: brief noun/verb phrase, not a complete sentence
- Block tag order: `@constructor`, `@receiver`, `@param`, `@property`, `@return`, `@throws`, `@see`
- Required for every `public` type and every `public`/`protected` member
