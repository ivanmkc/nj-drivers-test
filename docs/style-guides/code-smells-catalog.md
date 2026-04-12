# Code Smells Catalog

> Source: https://luzkan.github.io/smells/ (based on Martin Fowler's Refactoring)

## Bloaters -- Too Much

### Large Class
Combination of long method and parameter list issues at class level. A class is doing too much.

### Long Method
Methods with excessive line counts reducing comprehensibility. Extract smaller focused methods.

### Long Parameter List
Functions with three or more parameters. Group related parameters into objects.

### Primitive Obsession
Using primitives to simulate more abstract concepts. Replace with small value objects.

### Data Clump
Variables repeatedly passed together rather than grouped in objects. Extract a class.

## Dispensables -- Unnecessary Code

### Dead Code
Code never executed during program execution. Delete it.

### Duplicated Code
Redundant code identified as one of the worst smells. Extract shared methods/classes.

### Lazy Element
Code elements insufficient to justify their existence. Inline or remove.

### Speculative Generality
Features created anticipating future needs that never materialize. Remove unused abstractions.

### "What" Comment
Comments that describe what code does rather than why. The code should be self-explanatory.

## Object-Oriented Abusers

### Alternative Classes with Different Interfaces
Classes with identical functionality but different APIs. Unify the interface.

### Base Class Depends on Subclass
Parent classes improperly dependent on child implementations. Invert the dependency.

### Inappropriate Static
Overuse of static methods when instance methods are preferable.

### Refused Bequest
Subclasses inheriting but using only a subset of parent methods. Reconsider hierarchy.

### Temporary Field
Variables created only for specific situations. Extract into a separate class.

## Change Preventers

### Divergent Change
A single class is changed for many different reasons. Split by responsibility.

### Shotgun Surgery
A single change requires modifications across many classes. Consolidate related code.

### Parallel Inheritance Hierarchies
Creating a subclass in one hierarchy requires creating one in another. Merge hierarchies.

### Dubious Abstraction
Abstract interfaces that degrade over time. Reassess or remove.

## Couplers -- Excessive Coupling

### Feature Envy
Methods that use more features of other classes than their own. Move the method.

### Insider Trading
Classes excessively accessing each other's internal details. Reduce coupling.

### Message Chain
Requiring sequential calls through objects: `a.getB().getC().getD()`. Hide the chain.

### Middle Man
Classes performing only delegation to other classes. Remove the middleman.

### Indecent Exposure
Unnecessarily exposing internal implementation details. Restrict access.

## Data Dealers

### Global Data
Global scope variables freely accessible throughout codebase. Encapsulate.

### Hidden Dependencies
Classes silently resolving dependencies internally. Use dependency injection.

### Tramp Data
Data passed through long chains of methods that don't use it. Restructure.

### Mutable Data
Mutable variables causing unexpected failures in other code. Prefer immutability.

## Obfuscators -- Hard to Understand

### Clever Code
Implementation that prioritizes cleverness over clarity. Simplify.

### Obscured Intent
Code whose purpose is unclear. Rename, restructure, or document.

### Complicated Boolean Expression
Boolean expressions too complex to understand at a glance. Extract named predicates.

### Status Variable
Mutable primitives tracking state through a method. Replace with control flow.

### Vertical Separation
Variables declared far from their first use. Move declarations closer.

## Lexical Abusers -- Naming Problems

### Fallacious Comment
Comments that are outdated or misleading after code changes. Update or remove.

### Fallacious Method Name
Method names that don't reflect what the method actually does. Rename.

### Inconsistent Names
Different naming patterns for similar concepts. Standardize.

### Magic Number
Numeric literals without meaningful names. Extract as named constants.

### Uncommunicative Name
Names that fail to convey meaningful intent. Choose descriptive names.

### Boolean Blindness
Boolean parameters where true/false semantics are unclear. Use enums or named arguments.

### Type Embedded in Name
Variable names with explicit type prefixes or suffixes (Hungarian notation). Remove type info.

## Functional Abusers

### Imperative Loops
Loop constructs that could be replaced with functional alternatives (map, filter, reduce).

### Side Effects
Functions that modify state outside their scope. Prefer pure functions.

## Conditional Logic Smells

### Callback Hell
Deeply nested callback structures. Flatten with promises/async-await.

### Conditional Complexity
Lengthy cascading switch statements or if/else chains. Replace with polymorphism.

### Flag Argument
Function arguments that direct different behavior based on boolean value. Split into separate functions.

### Null Check
Excessive null/guard checks throughout codebase. Use Null Object pattern or optionals.

### Special Case
Complex conditionals checking for specific edge-case values. Extract special case objects.

## Other

### Combinatorial Explosion
Excessive code doing nearly identical operations with slight variations. Use parameterization.

### Required Setup or Teardown Code
Classes requiring extensive ceremony before use. Simplify initialization.

### Incomplete Library Class
Libraries missing necessary functionality. Extend via wrapper or adapter.
