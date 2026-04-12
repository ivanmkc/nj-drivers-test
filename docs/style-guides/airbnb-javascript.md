# Airbnb JavaScript Style Guide

> Source: https://github.com/airbnb/javascript

## References & Variables

- Always use `const`; use `let` only when reassignment is necessary
- Avoid `var` entirely due to function-scoping issues

## Objects & Arrays

- Use literal syntax (`{}` and `[]`)
- Use computed property names for dynamic keys
- Use object shorthand methods and property value shorthand
- Prefer object spread syntax over `Object.assign`

## Destructuring

- Extract values from objects and arrays to reduce repetitive access patterns

```javascript
// bad
function getFullName(user) {
  const firstName = user.firstName;
  const lastName = user.lastName;
  return `${firstName} ${lastName}`;
}

// good
function getFullName({ firstName, lastName }) {
  return `${firstName} ${lastName}`;
}
```

## Strings

- Use single quotes `''`
- Use template literals for interpolation
- Never use `eval()` on strings

## Functions

- Use named function expressions
- Use rest parameters (`...args`) instead of `arguments` object
- Use default parameters instead of mutating
- Never mutate or reassign parameters

## Arrow Functions

- Use for inline callbacks
- Omit braces for single-expression returns
- Keep braces for multiple statements

## Classes & Modules

- Always use `class` syntax over prototype manipulation
- Use `extends` for inheritance
- Always use `import`/`export` over `require`
- Avoid wildcard imports

## Comparison & Equality

- Use `===` and `!==` over `==` and `!=`
- Shortcuts for booleans; explicit for strings and numbers

## Formatting

- Use 2-space indentation
- 100-character line limits
- Include trailing commas in multiline structures
- Always use semicolons
- Require braces for all multiline blocks
- Place `else` on the same line as closing braces

## Iterators

- Prefer higher-order array methods (`map`, `filter`, `reduce`, `find`, `every`, `some`) over loops

## Naming Conventions

| Type | Convention | Example |
|------|-----------|---------|
| Files (single export) | Match export name | `CheckBox.js` |
| Classes | PascalCase | `class User {}` |
| Functions/variables | camelCase | `function getUser()` |
| Constants | UPPER_SNAKE_CASE | `const MAX_RETRIES` |
| Booleans | `is`/`has` prefix | `isVisible`, `hasError` |
