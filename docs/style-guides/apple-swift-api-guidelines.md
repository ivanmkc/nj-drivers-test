# Apple Swift API Design Guidelines

> Source: https://www.swift.org/documentation/api-design-guidelines/

## Core Principles

1. **Clarity at the point of use** is the most important goal
2. **Clarity over brevity** -- code should be explicit even if longer
3. **Write documentation** for every declaration; if you struggle to describe it simply, reconsider the API

## Naming

### Promote Clear Usage
- Include all words needed to avoid ambiguity
- Omit needless words that merely repeat type information
- Name entities by their **role** rather than type
- For weakly-typed parameters (`Any`, `Int`, `String`), precede with a noun describing the role

```swift
// GOOD
func remove(at position: Index) -> Element

// BAD -- what is "member"?
func remove(_ member: Element) -> Element?
```

### Strive for Fluent Usage
- Create grammatically natural phrases: `x.insert(y, at: z)` reads as "x, insert y at z"
- Begin factory methods with "make": `x.makeIterator()`
- Name functions by side effects:
  - No side effects = noun phrase: `x.distance(to: y)`
  - With side effects = imperative verb: `x.sort()`, `print(x)`

### Mutating/Nonmutating Pairs

| Mutating | Nonmutating |
|----------|-------------|
| `x.sort()` | `z = x.sorted()` |
| `x.append(y)` | `z = x.appending(y)` |
| `y.formUnion(z)` | `x = y.union(z)` |

- Verb-based: mutating is imperative; nonmutating uses "-ed"/"-ing" suffix
- Noun-based: nonmutating is the noun; mutating uses "form" prefix

### Terminology
- Avoid obscure terms when common words suffice
- Use terms of art strictly according to established meanings
- Avoid abbreviations
- Embrace precedent (e.g., `Array` not `List`)

## Conventions

### General
- Document complexity of computed properties that aren't O(1)
- Prefer methods and properties to free functions
- Case conventions: `UpperCamelCase` for types/protocols, `lowerCamelCase` for everything else
- Acronyms uniformly cased: `utf8Bytes`, `isRepresentableAsASCII`

### Parameters
- Choose parameter names for documentation readability
- Leverage defaulted parameters for common use cases
- Place parameters with defaults toward the end

### Argument Labels
- Omit labels when arguments cannot be usefully distinguished: `min(a, b)`
- Omit first label for value-preserving type conversions: `Int64(someUInt32)`
- Use labels for narrowing conversions: `init(truncating:)`, `init(saturating:)`
- Label all other arguments

```swift
// GOOD
func move(from start: Point, to end: Point)

// BAD
func move(start: Point, end: Point)
```

## Special Instructions

- Label tuple members and closure parameters for clarity
- Avoid ambiguity with polymorphism -- disambiguate overloads when `Element` is `Any`
