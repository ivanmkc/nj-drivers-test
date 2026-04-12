# Google Swift Style Guide

> Source: https://google.github.io/swift/

## Source File Basics

- Single type gets named after that type: `MyType.swift`
- Extensions adding protocol conformance: `TypeName+ProtocolName.swift`
- UTF-8 encoding; tab characters forbidden

## Source File Structure

- Imports ordered lexicographically, grouped by: modules, individual declarations, `@testable`
- Most files contain one top-level type
- Use `// MARK:` comments to organize sections; `// MARK: -` for dividers

## General Formatting

### Column Limit: 100 characters

### Braces (K&R style)
- No line break before opening `{`
- Line break after `{` and before `}`
- `} else {` stays on one line

### Semicolons
- Never used

### One Statement Per Line
- Single-statement blocks may be on one line:

```swift
guard let value = value else { return 0 }
defer { file.close() }
```

### Line-Wrapping
1. If it fits on one line, do that
2. Comma-delimited lists: all horizontal or all vertical, not mixed
3. Continuation lines indent exactly +2

### Trailing Commas
- Required in array/dictionary literals with each element on own line

## Naming

- Follow Apple's API Design Guidelines
- Use explicit access control (`private`, `fileprivate`, `internal`) -- not naming conventions
- Global constants: `lowerCamelCase` (no `k` prefix, no `UPPER_SNAKE_CASE`)
- Initializer arguments matching stored properties use same name with `self.` disambiguation
- Singleton properties use `shared` or `default`

## Programming Practices

### Properties
- Read-only computed properties omit `get` block

### Shorthand Types
- Use `[Element]` not `Array<Element>`
- Use `[Key: Value]` not `Dictionary<Key, Value>`
- Use `Wrapped?` not `Optional<Wrapped>`

### Force Unwrapping
- Strongly discouraged; include comments explaining safety invariants when used

### Error Handling
- Use error types for multiple failure states
- Force-`try!` forbidden except in tests and compile-time-guaranteed patterns

### Guard for Early Exits
- `guard` emphasizes special cases causing early exit; avoids pyramid of doom

```swift
func process(_ values: [Int]) throws -> Int {
  guard let first = values.first else {
    throw ProcessError.arrayWasEmpty
  }
  guard first >= 0 else {
    throw ProcessError.negativeValue
  }
  // main logic here
}
```

### Nesting and Namespacing
- Define "namespaces" via case-less enums:

```swift
enum Dimensions {
  static let tileMargin: CGFloat = 8
  static let tilePadding: CGFloat = 4
}
```

### Switch Statements
- Combine patterns into ranges or comma-delimited lists instead of fallthrough
- Place `let` individually before each matched element

### Trailing Closures
- Single closure as final argument: always trailing syntax
- Multiple closures: none use trailing syntax, all labeled

## Documentation Comments

- Use `///` format (never `/** */`)
- Begin with brief single-sentence summary
- Document parameters, returns, throws using tags
- Required for every `open`/`public` declaration

```swift
/// Returns the numeric value of the given digit.
///
/// - Parameters:
///   - digit: The Unicode scalar whose numeric value should be returned.
///   - radix: The radix used to compute the numeric value.
/// - Returns: The numeric value of the scalar.
func numericValue(of digit: UnicodeScalar, radix: Int = 10) -> Int { ... }
```
