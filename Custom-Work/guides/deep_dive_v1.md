# Complete Python Deep Dive Study Guide

## Table of Contents
1. [Python Object Model & Memory](#python-object-model--memory)
2. [Classes & Object Creation](#classes--object-creation)
3. [Descriptor Protocol](#descriptor-protocol)
4. [Metaclasses](#metaclasses)
5. [Iterator Protocol](#iterator-protocol)
6. [Generator Functions & yield](#generator-functions--yield)
7. [Context Managers](#context-managers)
8. [Decorators](#decorators)
9. [The Dunder Ecosystem](#the-dunder-ecosystem)
10. [Method Resolution Order (MRO)](#method-resolution-order-mro)
11. [Attribute Access](#attribute-access)
12. [Data Types Deep Dive](#data-types-deep-dive)
13. [Comprehensions & Functional Programming](#comprehensions--functional-programming)
14. [Memory Management & Garbage Collection](#memory-management--garbage-collection)
15. [Concurrency & Async](#concurrency--async)
16. [Global Interpreter Lock (GIL)](#global-interpreter-lock-gil)
17. [Import System & Modules](#import-system--modules)
18. [Exception Handling Deep Dive](#exception-handling-deep-dive)
19. [Built-in Functions Reference](#built-in-functions-reference)
20. [Common Patterns & Best Practices](#common-patterns--best-practices)

---

## Python Object Model & Memory

### How Python Objects Work
Every value in Python is an object. Even simple numbers like `42` are objects with methods and attributes.

```python
# Everything is an object
x = 42
print(type(x))           # <class 'int'>
print(x.__class__)       # <class 'int'>
print(id(x))             # Memory address
print(x.bit_length())    # Method on integer object

# Objects have identity, type, and value
a = [1, 2, 3]
b = [1, 2, 3]
c = a

print(a is b)        # False - different objects
print(a is c)        # True - same object
print(a == b)        # True - same value
print(id(a), id(b))  # Different memory addresses
```

### Object Identity and Equality
- `is` checks identity (same object in memory)
- `==` checks equality (same value)
- `id()` returns unique object identifier

```python
# Small integers are cached
a = 256
b = 256
print(a is b)    # True - cached

a = 257
b = 257
print(a is b)    # False - not cached (implementation dependent)

# String interning
s1 = "hello"
s2 = "hello"
print(s1 is s2)  # True - strings are interned

s1 = "hello world"
s2 = "hello world"
print(s1 is s2)  # May be True or False - depends on context
```

---

## Classes & Object Creation

### The Complete Object Creation Process

When you create an object with `MyClass()`, Python follows this order:

1. **`__new__`** - Creates the instance
2. **`__init__`** - Initializes the instance
3. Return the instance

```python
class Demo:
    def __new__(cls, *args, **kwargs):
        print(f"1. __new__ called with {cls}")
        instance = super().__new__(cls)
        print(f"2. __new__ created {instance}")
        return instance
    
    def __init__(self, value):
        print(f"3. __init__ called with {self}")
        self.value = value
        print(f"4. __init__ completed")

print("Creating instance:")
obj = Demo("test")
print(f"5. Object created: {obj}")
```

### `__new__` vs `__init__`

**`__new__`**:
- Static method that creates the object
- Returns the instance
- Rarely overridden unless creating immutable types or singletons

**`__init__`**:
- Instance method that initializes the object
- Returns None
- Most commonly overridden

```python
# Singleton pattern using __new__
class Singleton:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.initialized = True
            print("Initializing singleton")

s1 = Singleton()
s2 = Singleton()
print(s1 is s2)  # True

# Immutable type example
class Point:
    def __new__(cls, x, y):
        if x < 0 or y < 0:
            raise ValueError("Coordinates must be positive")
        instance = super().__new__(cls)
        return instance
    
    def __init__(self, x, y):
        self.x = x
        self.y = y
```

### `__slots__`

By default, Python stores instance attributes in a dictionary (`__dict__`). `__slots__` restricts attributes and saves memory.

```python
# Without slots
class RegularClass:
    def __init__(self, x, y):
        self.x = x
        self.y = y

# With slots
class SlottedClass:
    __slots__ = ['x', 'y']
    
    def __init__(self, x, y):
        self.x = x
        self.y = y

import sys

regular = RegularClass(1, 2)
slotted = SlottedClass(1, 2)

print(f"Regular size: {sys.getsizeof(regular)} bytes")
print(f"Slotted size: {sys.getsizeof(slotted)} bytes")

# Slots restrictions
try:
    regular.z = 3  # Works
    slotted.z = 3  # AttributeError
except AttributeError as e:
    print(f"Slots error: {e}")

# No __dict__ with slots
print(hasattr(regular, '__dict__'))  # True
print(hasattr(slotted, '__dict__'))  # False
```

### Class vs Instance Attributes

```python
class Counter:
    total_count = 0  # Class attribute
    
    def __init__(self, name):
        self.name = name          # Instance attribute
        Counter.total_count += 1  # Modify class attribute
    
    @classmethod
    def get_total(cls):
        return cls.total_count
    
    @property
    def instance_count(self):
        return Counter.total_count

c1 = Counter("first")
c2 = Counter("second")

print(f"Total: {Counter.total_count}")    # 2
print(f"Via class method: {Counter.get_total()}")  # 2
print(f"Via instance: {c1.instance_count}")       # 2

# Shadowing class attributes
c1.total_count = 999  # Creates instance attribute
print(f"c1.total_count: {c1.total_count}")      # 999 (instance)
print(f"Counter.total_count: {Counter.total_count}")  # 2 (class)
```

---

## Descriptor Protocol

Descriptors control attribute access. Any object defining `__get__`, `__set__`, or `__delete__` is a descriptor.

### Types of Descriptors

1. **Data descriptors**: Define `__get__` and (`__set__` or `__delete__`)
2. **Non-data descriptors**: Define only `__get__`

```python
class Descriptor:
    def __init__(self, name):
        self.name = name
    
    def __get__(self, instance, owner):
        print(f"Getting {self.name}")
        if instance is None:
            return self
        return instance.__dict__.get(self.name)
    
    def __set__(self, instance, value):
        print(f"Setting {self.name} to {value}")
        instance.__dict__[self.name] = value
    
    def __delete__(self, instance):
        print(f"Deleting {self.name}")
        del instance.__dict__[self.name]

class MyClass:
    attr = Descriptor('attr')
    
    def __init__(self, value):
        self.attr = value

obj = MyClass("test")
print(obj.attr)      # Calls __get__
obj.attr = "new"     # Calls __set__
del obj.attr         # Calls __delete__
```

### Property Implementation

`@property` is implemented using descriptors:

```python
class Temperature:
    def __init__(self, celsius=0):
        self._celsius = celsius
    
    def get_celsius(self):
        return self._celsius
    
    def set_celsius(self, value):
        if value < -273.15:
            raise ValueError("Temperature below absolute zero")
        self._celsius = value
    
    def get_fahrenheit(self):
        return self._celsius * 9/5 + 32
    
    def set_fahrenheit(self, value):
        self.celsius = (value - 32) * 5/9
    
    # Using property() function
    celsius = property(get_celsius, set_celsius)
    fahrenheit = property(get_fahrenheit, set_fahrenheit)

# Or using decorators (syntactic sugar)
class Temperature2:
    def __init__(self, celsius=0):
        self._celsius = celsius
    
    @property
    def celsius(self):
        return self._celsius
    
    @celsius.setter
    def celsius(self, value):
        if value < -273.15:
            raise ValueError("Temperature below absolute zero")
        self._celsius = value
    
    @property
    def fahrenheit(self):
        return self._celsius * 9/5 + 32
    
    @fahrenheit.setter
    def fahrenheit(self, value):
        self.celsius = (value - 32) * 5/9

temp = Temperature2(25)
print(temp.fahrenheit)  # 77.0
temp.fahrenheit = 86
print(temp.celsius)     # 30.0
```

### Validation Descriptor

```python
class ValidatedAttribute:
    def __init__(self, validator, name):
        self.validator = validator
        self.name = name
    
    def __get__(self, instance, owner):
        if instance is None:
            return self
        return instance.__dict__[self.name]
    
    def __set__(self, instance, value):
        if not self.validator(value):
            raise ValueError(f"Invalid value for {self.name}: {value}")
        instance.__dict__[self.name] = value

def positive_number(value):
    return isinstance(value, (int, float)) and value > 0

def non_empty_string(value):
    return isinstance(value, str) and len(value.strip()) > 0

class Person:
    age = ValidatedAttribute(positive_number, 'age')
    name = ValidatedAttribute(non_empty_string, 'name')
    
    def __init__(self, name, age):
        self.name = name
        self.age = age

try:
    p = Person("Alice", 25)
    p.age = -5  # ValueError
except ValueError as e:
    print(f"Validation error: {e}")
```

---

## Metaclasses

Metaclasses are "classes that create classes." In Python, classes are objects too, and metaclasses define how classes are created.

### Understanding the Relationship

```python
# Everything is an object
print(type(42))        # <class 'int'>
print(type(int))       # <class 'type'>
print(type(type))      # <class 'type'>

# Class creation process
class MyClass:
    pass

# This is equivalent to:
MyClass = type('MyClass', (), {})

print(type(MyClass))   # <class 'type'>
print(MyClass.__name__)  # MyClass
```

### Custom Metaclass

```python
class SingletonMeta(type):
    _instances = {}
    
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]

class Database(metaclass=SingletonMeta):
    def __init__(self, url):
        self.url = url
        print(f"Connecting to {url}")

db1 = Database("localhost")
db2 = Database("remote")
print(db1 is db2)  # True - same instance

# Attribute validation metaclass
class ValidatedMeta(type):
    def __new__(mcs, name, bases, namespace):
        # Add validation to all methods
        for key, value in list(namespace.items()):
            if callable(value) and not key.startswith('_'):
                namespace[key] = mcs.add_validation(value)
        return super().__new__(mcs, name, bases, namespace)
    
    @staticmethod
    def add_validation(func):
        def wrapper(*args, **kwargs):
            print(f"Calling {func.__name__}")
            return func(*args, **kwargs)
        return wrapper

class Service(metaclass=ValidatedMeta):
    def process(self):
        return "Processing..."
    
    def validate(self):
        return "Validating..."

service = Service()
service.process()   # Prints: Calling process
service.validate()  # Prints: Calling validate
```

### `__init_subclass__` (Modern Alternative)

Python 3.6+ provides `__init_subclass__` as a simpler alternative to metaclasses:

```python
class RegisteredClass:
    registry = {}
    
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.registry[cls.__name__] = cls
        print(f"Registered {cls.__name__}")

class ServiceA(RegisteredClass):
    pass

class ServiceB(RegisteredClass):
    pass

print(RegisteredClass.registry)
# {'ServiceA': <class '__main__.ServiceA'>, 'ServiceB': <class '__main__.ServiceB'>}
```

---

## Iterator Protocol

Objects that implement `__iter__` and `__next__` are iterators.

### Creating Custom Iterators

```python
class CountDown:
    def __init__(self, start):
        self.start = start
    
    def __iter__(self):
        return self
    
    def __next__(self):
        if self.start <= 0:
            raise StopIteration
        self.start -= 1
        return self.start + 1

# Usage
for num in CountDown(5):
    print(num)  # 5, 4, 3, 2, 1

# Manual iteration
countdown = CountDown(3)
iterator = iter(countdown)
print(next(iterator))  # 3
print(next(iterator))  # 2
print(next(iterator))  # 1
# next(iterator)  # StopIteration
```

### Iterator vs Iterable

```python
class NumberContainer:
    def __init__(self, numbers):
        self.numbers = numbers
    
    def __iter__(self):
        # Return a new iterator each time
        return NumberIterator(self.numbers)

class NumberIterator:
    def __init__(self, numbers):
        self.numbers = numbers
        self.index = 0
    
    def __iter__(self):
        return self
    
    def __next__(self):
        if self.index >= len(self.numbers):
            raise StopIteration
        value = self.numbers[self.index]
        self.index += 1
        return value

container = NumberContainer([1, 2, 3])

# Can iterate multiple times
for num in container:
    print(f"First: {num}")

for num in container:
    print(f"Second: {num}")
```

### Built-in Iterator Functions

```python
# iter() with callable and sentinel
import random

# Generate random numbers until we get 5
def random_generator():
    return random.randint(1, 10)

for num in iter(random_generator, 5):
    print(num)  # Stops when 5 is generated

# enumerate implementation
def my_enumerate(iterable, start=0):
    n = start
    for item in iterable:
        yield n, item
        n += 1

# zip implementation
def my_zip(*iterables):
    iterators = [iter(it) for it in iterables]
    while True:
        try:
            result = [next(it) for it in iterators]
            yield tuple(result)
        except StopIteration:
            return
```

---

## Generator Functions & yield

Generators are functions that use `yield` to produce values lazily.

### Basic Generator

```python
def simple_generator():
    print("Starting")
    yield 1
    print("Middle")
    yield 2
    print("End")
    yield 3

gen = simple_generator()
print(type(gen))  # <class 'generator'>

print(next(gen))  # Starting, then 1
print(next(gen))  # Middle, then 2
print(next(gen))  # End, then 3
# next(gen)  # StopIteration
```

### Generator State

Generators maintain state between yields:

```python
def fibonacci():
    a, b = 0, 1
    while True:
        yield a
        a, b = b, a + b

fib = fibonacci()
for _ in range(10):
    print(next(fib), end=' ')  # 0 1 1 2 3 5 8 13 21 34

# Generator expressions
squares = (x**2 for x in range(10))
print(type(squares))  # <class 'generator'>
print(list(squares))  # [0, 1, 4, 9, 16, 25, 36, 49, 64, 81]
```

### `yield from` (Delegation)

```python
def inner_generator():
    yield 1
    yield 2
    yield 3

def outer_generator():
    yield 'start'
    yield from inner_generator()  # Delegates to inner generator
    yield 'end'

list(outer_generator())  # ['start', 1, 2, 3, 'end']

# Equivalent without yield from
def outer_generator_manual():
    yield 'start'
    for value in inner_generator():
        yield value
    yield 'end'
```

### Send, Throw, Close

Generators support two-way communication:

```python
def coroutine():
    print("Starting")
    try:
        while True:
            value = yield
            print(f"Received: {value}")
    except GeneratorExit:
        print("Generator closing")
    finally:
        print("Cleanup")

gen = coroutine()
next(gen)  # Prime the generator
gen.send("hello")
gen.send("world")
gen.close()  # Raises GeneratorExit

# Generator with return value
def generator_with_return():
    yield 1
    yield 2
    return "done"

gen = generator_with_return()
print(next(gen))  # 1
print(next(gen))  # 2
try:
    next(gen)
except StopIteration as e:
    print(f"Return value: {e.value}")  # done
```

---

## Context Managers

Context managers use `__enter__` and `__exit__` to manage resources.

### Basic Context Manager

```python
class FileManager:
    def __init__(self, filename, mode):
        self.filename = filename
        self.mode = mode
        self.file = None
    
    def __enter__(self):
        print(f"Opening {self.filename}")
        self.file = open(self.filename, self.mode)
        return self.file
    
    def __exit__(self, exc_type, exc_value, traceback):
        print(f"Closing {self.filename}")
        if self.file:
            self.file.close()
        
        if exc_type is not None:
            print(f"Exception occurred: {exc_type.__name__}: {exc_value}")
        
        # Return False to propagate exceptions
        return False

# Usage
with FileManager('test.txt', 'w') as f:
    f.write("Hello, World!")
```

### Exception Handling in Context Managers

```python
class DatabaseTransaction:
    def __init__(self):
        self.transaction_active = False
    
    def __enter__(self):
        print("Starting transaction")
        self.transaction_active = True
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type is None:
            print("Committing transaction")
        else:
            print(f"Rolling back transaction due to {exc_type.__name__}")
        
        self.transaction_active = False
        
        # Return True to suppress exceptions
        if exc_type is ValueError:
            print("Handled ValueError, continuing...")
            return True
        
        return False

# Successful transaction
with DatabaseTransaction() as db:
    print("Doing database work...")

# Transaction with handled exception
with DatabaseTransaction() as db:
    raise ValueError("Something went wrong")
print("Continuing after handled exception")

# Transaction with unhandled exception
try:
    with DatabaseTransaction() as db:
        raise RuntimeError("Critical error")
except RuntimeError:
    print("Caught unhandled exception")
```

### `contextlib` Module

```python
from contextlib import contextmanager, closing, suppress
import socket

# @contextmanager decorator
@contextmanager
def temporary_value(obj, attr, new_value):
    old_value = getattr(obj, attr)
    setattr(obj, attr, new_value)
    try:
        yield obj
    finally:
        setattr(obj, attr, old_value)

class Config:
    debug = False

config = Config()
print(f"Before: {config.debug}")

with temporary_value(config, 'debug', True):
    print(f"Inside: {config.debug}")

print(f"After: {config.debug}")

# suppress context manager
with suppress(FileNotFoundError):
    open('nonexistent.txt').read()
print("File not found, but we continued")

# Multiple context managers
with open('file1.txt', 'w') as f1, open('file2.txt', 'w') as f2:
    f1.write("File 1")
    f2.write("File 2")
```

---

## Decorators

Decorators are functions that modify other functions or classes.

### Function Decorators

```python
def timing_decorator(func):
    import time
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(f"{func.__name__} took {end - start:.4f} seconds")
        return result
    return wrapper

@timing_decorator
def slow_function():
    import time
    time.sleep(1)
    return "Done"

slow_function()  # Prints timing information

# Decorator with parameters
def retry(max_attempts=3):
    def decorator(func):
        def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts - 1:
                        raise
                    print(f"Attempt {attempt + 1} failed: {e}")
        return wrapper
    return decorator

@retry(max_attempts=2)
def unreliable_function():
    import random
    if random.random() < 0.7:
        raise ValueError("Random failure")
    return "Success"
```

### Class Decorators

```python
def singleton(cls):
    instances = {}
    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]
    return get_instance

@singleton
class Database:
    def __init__(self, url):
        self.url = url

db1 = Database("localhost")
db2 = Database("remote")
print(db1 is db2)  # True

# Property decorator implementation
class property_decorator:
    def __init__(self, func):
        self.func = func
        self.setter_func = None
    
    def __get__(self, instance, owner):
        if instance is None:
            return self
        return self.func(instance)
    
    def __set__(self, instance, value):
        if self.setter_func is None:
            raise AttributeError("Can't set attribute")
        self.setter_func(instance, value)
    
    def setter(self, func):
        self.setter_func = func
        return self

class Circle:
    def __init__(self, radius):
        self._radius = radius
    
    @property_decorator
    def area(self):
        return 3.14159 * self._radius ** 2
```

### Method Decorators

```python
class MethodDecorators:
    @staticmethod
    def static_method():
        return "Static method called"
    
    @classmethod
    def class_method(cls):
        return f"Class method called on {cls.__name__}"
    
    @property
    def property_method(self):
        return "Property accessed"

# functools.wraps preserves metadata
from functools import wraps

def logged(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        print(f"Calling {func.__name__}")
        return func(*args, **kwargs)
    return wrapper

@logged
def example_function():
    """This is an example function."""
    return "result"

print(example_function.__name__)  # example_function (not wrapper)
print(example_function.__doc__)   # This is an example function.
```

---

## The Dunder Ecosystem

"Dunder" methods (double underscore) define how objects behave with built-in operations.

### Arithmetic Operations

```python
class Vector:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    def __add__(self, other):
        return Vector(self.x + other.x, self.y + other.y)
    
    def __sub__(self, other):
        return Vector(self.x - other.x, self.y - other.y)
    
    def __mul__(self, scalar):
        return Vector(self.x * scalar, self.y * scalar)
    
    def __rmul__(self, scalar):
        # Reverse multiplication (scalar * vector)
        return self.__mul__(scalar)
    
    def __truediv__(self, scalar):
        return Vector(self.x / scalar, self.y / scalar)
    
    def __abs__(self):
        return (self.x ** 2 + self.y ** 2) ** 0.5
    
    def __neg__(self):
        return Vector(-self.x, -self.y)
    
    def __repr__(self):
        return f"Vector({self.x}, {self.y})"

v1 = Vector(3, 4)
v2 = Vector(1, 2)

print(v1 + v2)    # Vector(4, 6)
print(v1 - v2)    # Vector(2, 2)
print(v1 * 2)     # Vector(6, 8)
print(3 * v1)     # Vector(9, 12) - uses __rmul__
print(abs(v1))    # 5.0
print(-v1)        # Vector(-3, -4)
```

### Comparison Operations

```python
class Student:
    def __init__(self, name, grade):
        self.name = name
        self.grade = grade
    
    def __eq__(self, other):
        return self.grade == other.grade
    
    def __lt__(self, other):
        return self.grade < other.grade
    
    def __le__(self, other):
        return self.grade <= other.grade
    
    def __gt__(self, other):
        return self.grade > other.grade
    
    def __ge__(self, other):
        return self.grade >= other.grade
    
    def __hash__(self):
        # Needed if object will be used in sets/dict keys
        return hash((self.name, self.grade))
    
    def __repr__(self):
        return f"Student('{self.name}', {self.grade})"

students = [
    Student("Alice", 85),
    Student("Bob", 92),
    Student("Charlie", 78)
]

print(sorted(students))  # Sorts by grade using __lt__
print(students[0] == students[1])  # False
print(students[1] > students[0])   # True

# Using in sets (requires __hash__ and __eq__)
unique_students = set(students)
```

### Container Operations

```python
class CustomList:
    def __init__(self, items=None):
        self.items = items or []
    
    def __len__(self):
        return len(self.items)
    
    def __getitem__(self, index):
        return self.items[index]
    
    def __setitem__(self, index, value):
        self.items[index] = value
    
    def __delitem__(self, index):
        del self.items[index]
    
    def __contains__(self, item):
        return item in self.items
    
    def __iter__(self):
        return iter(self.items)
    
    def __reversed__(self):
        return reversed(self.items)
    
    def __repr__(self):
        return f"CustomList({self.items})"

custom = CustomList([1, 2, 3, 4, 5])

print(len(custom))      # 5
print(custom[2])        # 3
custom[2] = 99
print(custom)           # CustomList([1, 2, 99, 4, 5])

print(3 in custom)      # False
print(99 in custom)     # True

for item in custom:
    print(item, end=' ')  # 1 2 99 4 5

for item in reversed(custom):
    print(item, end=' ')  # 5 4 99 2 1
```

### Callable Objects

```python
class Multiplier:
    def __init__(self, factor):
        self.factor = factor
    
    def __call__(self, value):
        return value * self.factor

# Object becomes callable
double = Multiplier(2)
print(double(5))      # 10
print(callable(double))  # True

# Function-like behavior
numbers = [1, 2, 3, 4, 5]
doubled = list(map(double, numbers))
print(doubled)        # [2, 4, 6, 8, 10]
```

### String Representation

```python
class Person:
    def __init__(self, name, age):
        self.name = name
        self.age = age
    
    def __str__(self):
        # Human-readable string (for end users)
        return f"{self.name} ({self.age} years old)"
    
    def __repr__(self):
        # Developer-friendly representation (for debugging)
        return f"Person('{self.name}', {self.age})"
    
    def __format__(self, format_spec):
        # Custom formatting
        if format_spec == 'formal':
            return f"Mr./Ms. {self.name}"
        elif format_spec == 'age_only':
            return str(self.age)
        return str(self)

person = Person("Alice", 30)

print(person)           # Alice (30 years old) - __str__
print(repr(person))     # Person('Alice', 30) - __repr__
print(f"{person:formal}")     # Mr./Ms. Alice
print(f"{person:age_only}")   # 30
```

---

## Method Resolution Order (MRO)

MRO determines the order in which Python searches for methods in inheritance hierarchies. Python uses the C3 linearization algorithm.

### Simple Inheritance

```python
class A:
    def method(self):
        print("A.method")

class B(A):
    def method(self):
        print("B.method")
        super().method()

class C(A):
    def method(self):
        print("C.method")
        super().method()

class D(B, C):  # Multiple inheritance
    def method(self):
        print("D.method")
        super().method()

print(D.__mro__)
# (<class '__main__.D'>, <class '__main__.B'>, <class '__main__.C'>, <class '__main__.A'>, <class 'object'>)

d = D()
d.method()
# Output:
# D.method
# B.method
# C.method
# A.method
```

### Diamond Problem Resolution

```python
class Base:
    def __init__(self):
        print("Base.__init__")

class Left(Base):
    def __init__(self):
        print("Left.__init__")
        super().__init__()

class Right(Base):
    def __init__(self):
        print("Right.__init__")
        super().__init__()

class Child(Left, Right):
    def __init__(self):
        print("Child.__init__")
        super().__init__()

print("MRO:", Child.__mro__)
# MRO: (<class '__main__.Child'>, <class '__main__.Left'>, <class '__main__.Right'>, <class '__main__.Base'>, <class 'object'>)

child = Child()
# Output:
# Child.__init__
# Left.__init__
# Right.__init__
# Base.__init__  (only called once!)
```

### Cooperative Inheritance

```python
class LoggingMixin:
    def __init__(self, *args, **kwargs):
        print(f"LoggingMixin: {self.__class__.__name__}")
        super().__init__(*args, **kwargs)

class ValidationMixin:
    def __init__(self, *args, **kwargs):
        print(f"ValidationMixin: {self.__class__.__name__}")
        super().__init__(*args, **kwargs)

class Person:
    def __init__(self, name, age):
        print(f"Person: {name}, {age}")
        self.name = name
        self.age = age

class Employee(LoggingMixin, ValidationMixin, Person):
    def __init__(self, name, age, employee_id):
        print(f"Employee: {employee_id}")
        self.employee_id = employee_id
        super().__init__(name, age)

print("MRO:", Employee.__mro__)
emp = Employee("Alice", 30, "E001")
```

### Method Resolution with `super()`

```python
class A:
    def method(self):
        print("A")
        return "A"

class B(A):
    def method(self):
        print("B")
        result = super().method()
        return f"B->{result}"

class C(A):
    def method(self):
        print("C")
        result = super().method()
        return f"C->{result}"

class D(B, C):
    def method(self):
        print("D")
        result = super().method()
        return f"D->{result}"

# Understanding what super() calls
d = D()
result = d.method()
print(f"Final result: {result}")
# Output:
# D
# B
# C
# A
# Final result: D->B->C->A
```

---

## Attribute Access

Python has a complex attribute access mechanism with multiple hooks for customization.

### Attribute Access Order

1. `__getattribute__` (always called)
2. Data descriptors from type(obj).__mro__
3. Instance __dict__
4. Non-data descriptors from type(obj).__mro__
5. Class __dict__
6. `__getattr__` (if attribute not found)

```python
class AttributeDemo:
    class_attr = "class_attribute"
    
    def __init__(self):
        self.instance_attr = "instance_attribute"
    
    def __getattribute__(self, name):
        print(f"__getattribute__: {name}")
        return super().__getattribute__(name)
    
    def __getattr__(self, name):
        print(f"__getattr__: {name} (not found)")
        return f"default_value_for_{name}"
    
    def __setattr__(self, name, value):
        print(f"__setattr__: {name} = {value}")
        super().__setattr__(name, value)
    
    def __delattr__(self, name):
        print(f"__delattr__: {name}")
        super().__delattr__(name)

obj = AttributeDemo()
print(obj.instance_attr)  # Found in instance __dict__
print(obj.class_attr)     # Found in class __dict__
print(obj.missing_attr)   # Calls __getattr__

obj.new_attr = "new"      # Calls __setattr__
del obj.new_attr          # Calls __delattr__
```

### `hasattr`, `getattr`, `setattr`, `delattr`

```python
class FlexibleObject:
    def __init__(self):
        self.existing = "exists"
    
    def __getattr__(self, name):
        if name.startswith('dynamic_'):
            return f"Dynamic attribute: {name}"
        raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")

obj = FlexibleObject()

# hasattr() catches AttributeError
print(hasattr(obj, 'existing'))        # True
print(hasattr(obj, 'dynamic_test'))    # True
print(hasattr(obj, 'nonexistent'))     # False

# getattr() with default
print(getattr(obj, 'existing'))           # exists
print(getattr(obj, 'missing', 'default')) # default
print(getattr(obj, 'dynamic_hello'))      # Dynamic attribute: dynamic_hello

# setattr() and delattr()
setattr(obj, 'new_attr', 'new_value')
print(obj.new_attr)                       # new_value

delattr(obj, 'new_attr')
print(hasattr(obj, 'new_attr'))           # False
```

### Slots and Attribute Access

```python
class SlottedClass:
    __slots__ = ['x', 'y', '_z']
    
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self._z = x + y
    
    @property
    def z(self):
        return self._z
    
    def __setattr__(self, name, value):
        if name in ('x', 'y'):
            super().__setattr__(name, value)
            if hasattr(self, 'x') and hasattr(self, 'y'):
                super().__setattr__('_z', self.x + self.y)
        else:
            super().__setattr__(name, value)

obj = SlottedClass(3, 4)
print(obj.z)    # 7
obj.x = 10
print(obj.z)    # 14

# Can't add new attributes to slotted classes
try:
    obj.new_attr = "test"
except AttributeError as e:
    print(f"Slots restriction: {e}")
```

---

## Data Types Deep Dive

### Integers

```python
# Integer implementation details
import sys

# Small integers are cached
a = 256
b = 256
print(a is b)  # True

a = 257
b = 257
print(a is b)  # False (may vary by implementation)

# Arbitrary precision
big_int = 2 ** 1000
print(f"Big integer: {big_int}")
print(f"Bit length: {big_int.bit_length()}")

# Integer methods
x = 42
print(f"Binary: {bin(x)}")
print(f"Hex: {hex(x)}")
print(f"Octal: {oct(x)}")
print(f"Bit count: {x.bit_count()}")  # Python 3.10+

# Different number bases
print(int('1010', 2))    # Binary: 10
print(int('ff', 16))     # Hex: 255
print(int('77', 8))      # Octal: 63
```

### Strings

```python
# String internment
a = "hello"
b = "hello"
print(a is b)  # True - strings are interned

# But not always
a = "hello world"
b = "hello world"
print(a is b)  # May be False

# Force internment
import sys
a = sys.intern("hello world")
b = sys.intern("hello world")
print(a is b)  # True

# String encoding
text = "Hello, ä¸–ç•Œ"
encoded = text.encode('utf-8')
print(f"Bytes: {encoded}")
print(f"Decoded: {encoded.decode('utf-8')}")

# String formatting details
name = "Alice"
age = 30

# f-strings (fastest)
result1 = f"Name: {name}, Age: {age}"

# .format() method
result2 = "Name: {}, Age: {}".format(name, age)
result3 = "Name: {name}, Age: {age}".format(name=name, age=age)

# % formatting (old style)
result4 = "Name: %s, Age: %d" % (name, age)

print(all(r == result1 for r in [result2, result3, result4]))  # True
```

### Lists

```python
# List implementation details
import sys

# Lists over-allocate for efficiency
lst = []
for i in range(10):
    print(f"Length: {len(lst)}, Capacity: {sys.getsizeof(lst)}")
    lst.append(i)

# List comprehensions vs loops
import timeit

# List comprehension (faster)
def list_comp():
    return [x**2 for x in range(1000)]

# Regular loop
def regular_loop():
    result = []
    for x in range(1000):
        result.append(x**2)
    return result

# Timing comparison
comp_time = timeit.timeit(list_comp, number=1000)
loop_time = timeit.timeit(regular_loop, number=1000)
print(f"List comprehension: {comp_time:.4f}s")
print(f"Regular loop: {loop_time:.4f}s")

# List methods and their complexity
lst = [1, 2, 3, 4, 5]
lst.append(6)        # O(1) amortized
lst.insert(0, 0)     # O(n)
lst.remove(3)        # O(n)
lst.pop()            # O(1)
lst.pop(0)           # O(n)
print(lst.index(2))  # O(n)
```

### Dictionaries

```python
# Dictionary implementation (hash table)
d = {}

# Hash collisions and resolution
class BadHash:
    def __init__(self, value):
        self.value = value
    
    def __hash__(self):
        return 1  # All instances have same hash!
    
    def __eq__(self, other):
        return isinstance(other, BadHash) and self.value == other.value
    
    def __repr__(self):
        return f"BadHash({self.value})"

# All these objects hash to 1, causing collisions
bad_dict = {}
for i in range(5):
    bad_dict[BadHash(i)] = f"value_{i}"

print(bad_dict)  # Still works, but less efficient

# Dictionary views
d = {'a': 1, 'b': 2, 'c': 3}
keys = d.keys()
values = d.values()
items = d.items()

print(type(keys))    # <class 'dict_keys'>
print('a' in keys)   # True - O(1) lookup

# Views are dynamic
d['d'] = 4
print(list(keys))    # ['a', 'b', 'c', 'd']

# Dictionary merge operators (Python 3.9+)
d1 = {'a': 1, 'b': 2}
d2 = {'c': 3, 'd': 4}
merged = d1 | d2     # {'a': 1, 'b': 2, 'c': 3, 'd': 4}
d1 |= d2             # In-place merge
```

### Sets

```python
# Set implementation (hash table)
s = {1, 2, 3, 4, 5}

# Set operations
s1 = {1, 2, 3}
s2 = {3, 4, 5}

print(s1 | s2)       # Union: {1, 2, 3, 4, 5}
print(s1 & s2)       # Intersection: {3}
print(s1 - s2)       # Difference: {1, 2}
print(s1 ^ s2)       # Symmetric difference: {1, 2, 4, 5}

# Set comprehensions
squares = {x**2 for x in range(10)}
print(squares)       # {0, 1, 4, 9, 16, 25, 36, 49, 64, 81}

# Frozenset (immutable set)
fs = frozenset([1, 2, 3])
print(hash(fs))      # Hashable, can be dict key

nested_sets = {frozenset([1, 2]), frozenset([3, 4])}
print(nested_sets)
```

---

## Comprehensions & Functional Programming

### Advanced List Comprehensions

```python
# Nested list comprehensions
matrix = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]

# Flatten matrix
flattened = [item for row in matrix for item in row]
print(flattened)  # [1, 2, 3, 4, 5, 6, 7, 8, 9]

# Transpose matrix
transposed = [[row[i] for row in matrix] for i in range(len(matrix[0]))]
print(transposed)  # [[1, 4, 7], [2, 5, 8], [3, 6, 9]]

# Multiple conditions
numbers = [x for x in range(100) if x % 2 == 0 if x % 3 == 0]
print(numbers[:10])  # [0, 6, 12, 18, 24, 30, 36, 42, 48, 54]

# Conditional expressions
result = [x if x > 0 else 0 for x in [-2, -1, 0, 1, 2]]
print(result)  # [0, 0, 0, 1, 2]
```

### Dictionary and Set Comprehensions

```python
# Advanced dictionary comprehensions
words = ['hello', 'world', 'python', 'programming']

# Multiple transformations
word_stats = {
    word: {
        'length': len(word),
        'vowels': sum(1 for c in word if c in 'aeiou'),
        'consonants': sum(1 for c in word if c.isalpha() and c not in 'aeiou')
    }
    for word in words
}

print(word_stats['python'])
# {'length': 6, 'vowels': 1, 'consonants': 5}

# Conditional dictionary comprehension
numbers = range(10)
even_squares = {x: x**2 for x in numbers if x % 2 == 0}
print(even_squares)  # {0: 0, 2: 4, 4: 16, 6: 36, 8: 64}

# Set comprehensions with functions
def is_prime(n):
    if n < 2:
        return False
    return all(n % i != 0 for i in range(2, int(n**0.5) + 1))

primes = {n for n in range(100) if is_prime(n)}
print(sorted(primes)[:10])  # [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]
```

### Functional Programming Tools

```python
from functools import reduce, partial, lru_cache
from itertools import chain, combinations, permutations, product

# reduce() function
numbers = [1, 2, 3, 4, 5]
product_result = reduce(lambda x, y: x * y, numbers)
print(product_result)  # 120

# partial() for function currying
def multiply(x, y, z):
    return x * y * z

double = partial(multiply, 2)  # Fix first argument
result = double(3, 4)  # multiply(2, 3, 4)
print(result)  # 24

# lru_cache for memoization
@lru_cache(maxsize=128)
def fibonacci(n):
    if n < 2:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

print([fibonacci(i) for i in range(10)])
print(fibonacci.cache_info())  # CacheInfo(hits=8, misses=10, maxsize=128, currsize=10)

# itertools combinations
items = ['a', 'b', 'c', 'd']
for combo in combinations(items, 2):
    print(combo)  # ('a', 'b'), ('a', 'c'), ('a', 'd'), ('b', 'c'), ('b', 'd'), ('c', 'd')

# itertools chain for flattening
nested = [[1, 2], [3, 4], [5, 6]]
flattened = list(chain.from_iterable(nested))
print(flattened)  # [1, 2, 3, 4, 5, 6]

# Generator expressions with itertools
from itertools import islice, cycle, count

# Infinite sequences
infinite_counter = count(1, 2)  # 1, 3, 5, 7, ...
first_10_odds = list(islice(infinite_counter, 10))
print(first_10_odds)  # [1, 3, 5, 7, 9, 11, 13, 15, 17, 19]

# Cycling through values
colors = cycle(['red', 'green', 'blue'])
first_10_colors = list(islice(colors, 10))
print(first_10_colors)  # ['red', 'green', 'blue', 'red', 'green', 'blue', 'red', 'green', 'blue', 'red']
```

---

## Memory Management & Garbage Collection

### Reference Counting

```python
import sys

# Reference counting
a = [1, 2, 3]
print(sys.getrefcount(a))  # 2 (a + temporary reference in getrefcount)

b = a
print(sys.getrefcount(a))  # 3

del b
print(sys.getrefcount(a))  # 2

# Circular references
class Node:
    def __init__(self, value):
        self.value = value
        self.parent = None
        self.children = []
    
    def add_child(self, child):
        child.parent = self
        self.children.append(child)

root = Node("root")
child = Node("child")
root.add_child(child)  # Creates circular reference

print(f"Root refcount: {sys.getrefcount(root)}")
print(f"Child refcount: {sys.getrefcount(child)}")

# Even after deleting root, circular reference remains
# (until garbage collector runs)
```

### Garbage Collection

```python
import gc
import weakref

# Garbage collection for circular references
class TrackableObject:
    def __init__(self, name):
        self.name = name
        print(f"Creating {name}")
    
    def __del__(self):
        print(f"Deleting {self.name}")

# Create circular reference
obj1 = TrackableObject("obj1")
obj2 = TrackableObject("obj2")
obj1.ref = obj2
obj2.ref = obj1

# Remove direct references
del obj1, obj2

# Objects still exist due to circular references
print("After del, before gc:")
print(f"Garbage objects: {len(gc.garbage)}")

# Force garbage collection
collected = gc.collect()
print(f"Collected {collected} objects")

# Weakref to avoid circular references
class Parent:
    def __init__(self, name):
        self.name = name
        self.children = []
    
    def add_child(self, child):
        self.children.append(child)
        child.parent = weakref.ref(self)  # Weak reference

class Child:
    def __init__(self, name):
        self.name = name
        self.parent = None
    
    def get_parent(self):
        if self.parent is not None:
            return self.parent()  # Call weak reference
        return None

parent = Parent("parent")
child = Child("child")
parent.add_child(child)

print(f"Child's parent: {child.get_parent().name}")

del parent
# Child's parent weak reference becomes None
print(f"After parent deletion: {child.get_parent()}")
```

### Memory Optimization

```python
import sys
from array import array

# Regular list vs array for numeric data
regular_list = [i for i in range(1000)]
int_array = array('i', range(1000))  # 'i' for signed int

print(f"List size: {sys.getsizeof(regular_list)} bytes")
print(f"Array size: {sys.getsizeof(int_array)} bytes")

# __slots__ for memory efficiency
class RegularClass:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

class SlottedClass:
    __slots__ = ['x', 'y', 'z']
    
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

regular = RegularClass(1, 2, 3)
slotted = SlottedClass(1, 2, 3)

print(f"Regular object: {sys.getsizeof(regular)} bytes")
print(f"Slotted object: {sys.getsizeof(slotted)} bytes")

# Memory profiling
import tracemalloc

tracemalloc.start()

# Some memory-intensive operation
data = [i**2 for i in range(10000)]

current, peak = tracemalloc.get_traced_memory()
print(f"Current memory usage: {current / 1024 / 1024:.2f} MB")
print(f"Peak memory usage: {peak / 1024 / 1024:.2f} MB")

tracemalloc.stop()
```

---

## Concurrency & Async

### Threading

```python
import threading
import time
import queue

# Basic threading
def worker(name, duration):
    print(f"{name} starting")
    time.sleep(duration)
    print(f"{name} finished")

# Create and start threads
threads = []
for i in range(3):
    t = threading.Thread(target=worker, args=(f"Worker-{i}", 1))
    t.start()
    threads.append(t)

# Wait for all threads to complete
for t in threads:
    t.join()

print("All threads completed")

# Thread-safe operations with Lock
counter = 0
counter_lock = threading.Lock()

def increment_counter():
    global counter
    for _ in range(100000):
        with counter_lock:
            counter += 1

threads = []
for _ in range(5):
    t = threading.Thread(target=increment_counter)
    t.start()
    threads.append(t)

for t in threads:
    t.join()

print(f"Final counter value: {counter}")  # Should be 500000

# Producer-Consumer with Queue
def producer(q):
    for i in range(5):
        item = f"item-{i}"
        q.put(item)
        print(f"Produced {item}")
        time.sleep(0.1)
    q.put(None)  # Sentinel value

def consumer(q):
    while True:
        item = q.get()
        if item is None:
            break
        print(f"Consumed {item}")
        time.sleep(0.2)
        q.task_done()

q = queue.Queue()
t1 = threading.Thread(target=producer, args=(q,))
t2 = threading.Thread(target=consumer, args=(q,))

t1.start()
t2.start()

t1.join()
t2.join()
```

### Async/Await

```python
import asyncio
import aiohttp
import time

# Basic async function
async def async_worker(name, duration):
    print(f"{name} starting")
    await asyncio.sleep(duration)  # Non-blocking sleep
    print(f"{name} finished")
    return f"Result from {name}"

# Running async functions
async def main():
    # Sequential execution
    start = time.time()
    result1 = await async_worker("Worker-1", 1)
    result2 = await async_worker("Worker-2", 1)
    sequential_time = time.time() - start
    
    # Concurrent execution
    start = time.time()
    results = await asyncio.gather(
        async_worker("Worker-3", 1),
        async_worker("Worker-4", 1),
        async_worker("Worker-5", 1)
    )
    concurrent_time = time.time() - start
    
    print(f"Sequential time: {sequential_time:.2f}s")
    print(f"Concurrent time: {concurrent_time:.2f}s")
    print(f"Results: {results}")

# Run the async main function
asyncio.run(main())

# Async context managers
class AsyncDatabase:
    def __init__(self, url):
        self.url = url
        self.connected = False
    
    async def __aenter__(self):
        print(f"Connecting to {self.url}")
        await asyncio.sleep(0.1)  # Simulate connection time
        self.connected = True
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        print("Disconnecting from database")
        await asyncio.sleep(0.1)  # Simulate cleanup time
        self.connected = False

async def database_operation():
    async with AsyncDatabase("localhost") as db:
        print(f"Database connected: {db.connected}")
        await asyncio.sleep(0.5)  # Simulate work

asyncio.run(database_operation())

# Async iterators
class AsyncRange:
    def __init__(self, start, stop):
        self.start = start
        self.stop = stop
    
    def __aiter__(self):
        return self
    
    async def __anext__(self):
        if self.start >= self.stop:
            raise StopAsyncIteration
        await asyncio.sleep(0.1)  # Simulate async work
        value = self.start
        self.start += 1
        return value

async def async_iteration():
    async for num in AsyncRange(0, 5):
        print(f"Async number: {num}")

asyncio.run(async_iteration())
```

### Coroutines and Event Loops

```python
import asyncio
import inspect

# Coroutine functions and objects
async def my_coroutine():
    await asyncio.sleep(1)
    return "Hello, Async!"

# Function is a coroutine function
print(inspect.iscoroutinefunction(my_coroutine))  # True

# Calling it creates a coroutine object
coro = my_coroutine()
print(inspect.iscoroutine(coro))  # True

# Must be awaited or run
result = asyncio.run(coro)
print(result)  # Hello, Async!

# Event loop management
async def background_task():
    while True:
        print("Background task running...")
        await asyncio.sleep(2)

async def main_with_background():
    # Start background task
    task = asyncio.create_task(background_task())
    
    # Do some main work
    for i in range(5):
        print(f"Main work: {i}")
        await asyncio.sleep(1)
    
    # Cancel background task
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        print("Background task cancelled")

asyncio.run(main_with_background())
```

---

## Global Interpreter Lock (GIL)

### Understanding the GIL

```python
import threading
import time
import multiprocessing

# CPU-bound task that shows GIL limitations
def cpu_bound_task(n):
    count = 0
    for i in range(n):
        count += i * i
    return count

# Threading (limited by GIL for CPU-bound tasks)
def test_threading():
    start = time.time()
    threads = []
    
    for _ in range(4):
        t = threading.Thread(target=cpu_bound_task, args=(1000000,))
        t.start()
        threads.append(t)
    
    for t in threads:
        t.join()
    
    threading_time = time.time() - start
    return threading_time

# Multiprocessing (bypasses GIL)
def test_multiprocessing():
    start = time.time()
    
    with multiprocessing.Pool(4) as pool:
        pool.map(cpu_bound_task, [1000000] * 4)
    
    multiprocessing_time = time.time() - start
    return multiprocessing_time

# Single-threaded baseline
def test_sequential():
    start = time.time()
    
    for _ in range(4):
        cpu_bound_task(1000000)
    
    sequential_time = time.time() - start
    return sequential_time

if __name__ == "__main__":
    sequential = test_sequential()
    threading_result = test_threading()
    multiprocessing_result = test_multiprocessing()
    
    print(f"Sequential: {sequential:.2f}s")
    print(f"Threading: {threading_result:.2f}s")
    print(f"Multiprocessing: {multiprocessing_result:.2f}s")
    
    # Threading may be slower due to GIL and context switching
    # Multiprocessing should be faster for CPU-bound tasks

# I/O-bound tasks benefit from threading despite GIL
import requests
import asyncio
import aiohttp

def io_bound_task(url):
    response = requests.get(url)
    return len(response.content)

urls = ["http://httpbin.org/delay/1"] * 5

# Sequential I/O
start = time.time()
results = [io_bound_task(url) for url in urls]
sequential_io = time.time() - start

# Threaded I/O (releases GIL during I/O)
start = time.time()
threads = []
for url in urls:
    t = threading.Thread(target=io_bound_task, args=(url,))
    t.start()
    threads.append(t)

for t in threads:
    t.join()
threading_io = time.time() - start

print(f"Sequential I/O: {sequential_io:.2f}s")
print(f"Threaded I/O: {threading_io:.2f}s")
```

---

## Import System & Modules

### Module Search Path

```python
import sys
import os

# Python searches for modules in this order
print("Module search path:")
for i, path in enumerate(sys.path):
    print(f"{i}: {path}")

# Current working directory
print(f"Current working directory: {os.getcwd()}")

# Adding to path at runtime
sys.path.insert(0, '/custom/module/path')

# Module attributes
import math
print(f"Module name: {math.__name__}")
print(f"Module file: {math.__file__}")
print(f"Module package: {getattr(math, '__package__', None)}")
```

### Import Mechanisms

```python
# Different import styles
import os
import os.path as path
from os import getcwd, listdir
from os.path import join, dirname
from collections import *  # Not recommended

# Conditional imports
try:
    import ujson as json  # Faster JSON library
except ImportError:
    import json

# Lazy imports
def get_numpy():
    import numpy as np
    return np

# Dynamic imports
module_name = "datetime"
datetime_module = __import__(module_name)
# Or using importlib
import importlib
datetime_module = importlib.import_module(module_name)

# Reloading modules (useful in development)
import importlib
import my_module
# After changing my_module.py
importlib.reload(my_module)
```

### Package Structure

```python
# Package structure example:
# mypackage/
#   __init__.py
#   core.py
#   utils/
#     __init__.py
#     helpers.py
#   tests/
#     __init__.py
#     test_core.py

# __init__.py controls package initialization
# mypackage/__init__.py
"""
from .core import main_function
from .utils.helpers import helper_function

__version__ = "1.0.0"
__all__ = ['main_function', 'helper_function']
"""

# Relative imports within packages
# From mypackage/core.py
from .utils.helpers import some_helper
from ..other_package import other_function

# Absolute imports
from mypackage.utils.helpers import some_helper
```

### Module Creation and Execution

```python
# Module-level code runs on first import
print("This runs when the module is imported")

# Conditional execution
if __name__ == "__main__":
    print("This runs only when script is executed directly")
    # Command-line interface code goes here

# Module docstring
"""
This is a module docstring.
It describes what this module does.
"""

# Module-level variables become module attributes
MODULE_CONSTANT = "This is a constant"
_private_variable = "By convention, this is private"

def public_function():
    """This function is part of the public API."""
    pass

def _private_function():
    """By convention, this function is private."""
    pass

# __all__ controls what's imported with "from module import *"
__all__ = ['MODULE_CONSTANT', 'public_function']
```

---

## Exception Handling Deep Dive

### Exception Hierarchy

```python
# Python exception hierarchy (simplified)
"""
BaseException
 +-- SystemExit
 +-- KeyboardInterrupt
 +-- GeneratorExit
 +-- Exception
      +-- StopIteration
      +-- ArithmeticError
      |    +-- FloatingPointError
      |    +-- OverflowError
      |    +-- ZeroDivisionError
      +-- AttributeError
      +-- EOFError
      +-- ImportError
      |    +-- ModuleNotFoundError
      +-- LookupError
      |    +-- IndexError
      |    +-- KeyError
      +-- NameError
      |    +-- UnboundLocalError
      +-- OSError
      |    +-- FileNotFoundError
      |    +-- PermissionError
      +-- RuntimeError
      |    +-- NotImplementedError
      |    +-- RecursionError
      +-- TypeError
      +-- ValueError
      |    +-- UnicodeError
      +-- Warning
           +-- DeprecationWarning
           +-- UserWarning
"""

# Custom exception hierarchy
class ApplicationError(Exception):
    """Base exception for application-specific errors."""
    pass

class ValidationError(ApplicationError):
    """Raised when validation fails."""
    pass

class DatabaseError(ApplicationError):
    """Raised when database operations fail."""
    pass

class ConnectionError(DatabaseError):
    """Raised when database connection fails."""
    pass

# Exception with additional attributes
class DetailedError(Exception):
    def __init__(self, message, error_code=None, details=None):
        super().__init__(message)
        self.error_code = error_code
        self.details = details or {}
    
    def __str__(self):
        result = super().__str__()
        if self.error_code:
            result += f" (Code: {self.error_code})"
        return result

try:
    raise DetailedError("Something went wrong", error_code="E001", 
                       details={"user_id": 123, "action": "login"})
except DetailedError as e:
    print(f"Error: {e}")
    print(f"Code: {e.error_code}")
    print(f"Details: {e.details}")
```

### Exception Chaining

```python
# Exception chaining with "from"
def process_data(data):
    try:
        return int(data)
    except ValueError as e:
        raise ValidationError(f"Invalid data: {data}") from e

try:
    result = process_data("invalid")
except ValidationError as e:
    print(f"Caught: {e}")
    print(f"Original cause: {e.__cause__}")
    print(f"Traceback includes both exceptions")

# Suppressing exception chaining
def suppress_chain():
    try:
        raise ValueError("Original error")
    except ValueError:
        raise RuntimeError("New error") from None  # Suppresses chaining

# Exception context (implicit chaining)
def implicit_chaining():
    try:
        raise ValueError("First error")
    except ValueError:
        raise RuntimeError("Second error")  # Automatically chained

try:
    implicit_chaining()
except RuntimeError as e:
    print(f"Exception: {e}")
    print(f"Context: {e.__context__}")
```

### Advanced Exception Handling

```python
import traceback
import sys
import logging

# Custom exception hook
def custom_exception_hook(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        # Handle Ctrl+C gracefully
        print("\nGracefully shutting down...")
        sys.exit(0)
    
    # Log all other exceptions
    logging.error("Uncaught exception", 
                 exc_info=(exc_type, exc_value, exc_traceback))

# Install custom exception hook
sys.excepthook = custom_exception_hook

# Exception groups (Python 3.11+)
# Note: This is a preview of Python 3.11 features
"""
try:
    raise ExceptionGroup("Multiple errors", [
        ValueError("Invalid value"),
        TypeError("Wrong type"),
        RuntimeError("Runtime issue")
    ])
except* ValueError as eg:
    print(f"Handling ValueError: {eg}")
except* TypeError as eg:
    print(f"Handling TypeError: {eg}")
"""

# Traceback manipulation
def get_traceback_info():
    try:
        raise ValueError("Test error")
    except ValueError:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        
        # Print formatted traceback
        traceback.print_exc()
        
        # Get traceback as string
        tb_str = traceback.format_exc()
        
        # Get specific traceback information
        tb_lines = traceback.format_tb(exc_traceback)
        
        return {
            'type': exc_type.__name__,
            'value': str(exc_value),
            'traceback': tb_str,
            'lines': tb_lines
        }

# Context managers for exception handling
class ExceptionLogger:
    def __init__(self, logger):
        self.logger = logger
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type is not None:
            self.logger.error(f"Exception occurred: {exc_type.__name__}: {exc_value}")
        return False  # Don't suppress exceptions

# Usage
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

with ExceptionLogger(logger):
    raise ValueError("This will be logged")
```

---

## Built-in Functions Reference

### Essential Built-ins

```python
# Type checking and conversion
print(isinstance(42, int))          # True
print(isinstance(42, (int, float))) # True
print(issubclass(bool, int))        # True

print(type(42))                     # <class 'int'>
print(type(42).__name__)            # 'int'

# Conversion functions
print(int("42"))                    # 42
print(float("3.14"))                # 3.14
print(str(42))                      # '42'
print(bool(0))                      # False
print(list("hello"))                # ['h', 'e', 'l', 'l', 'o']
print(tuple([1, 2, 3]))            # (1, 2, 3)
print(set([1, 2, 2, 3]))           # {1, 2, 3}
print(dict([('a', 1), ('b', 2)]))  # {'a': 1, 'b': 2}

# Numeric functions
print(abs(-42))                     # 42
print(divmod(17, 5))               # (3, 2)
print(pow(2, 3))                   # 8
print(pow(2, 3, 5))               # 3 (2^3 % 5)
print(round(3.14159, 2))          # 3.14

# Sequence functions
numbers = [1, 5, 3, 9, 2]
print(len(numbers))                # 5
print(max(numbers))                # 9
print(min(numbers))                # 1
print(sum(numbers))                # 20
print(sorted(numbers))             # [1, 2, 3, 5, 9]
print(reversed(numbers))           # <list_reverseiterator object>
print(list(reversed(numbers)))     # [2, 9, 3, 5, 1]

# Iterator functions
print(list(enumerate(['a', 'b', 'c'])))     # [(0, 'a'), (1, 'b'), (2, 'c')]
print(list(zip([1, 2, 3], ['a', 'b', 'c']))) # [(1, 'a'), (2, 'b'), (3, 'c')]
print(list(range(5)))                       # [0, 1, 2, 3, 4]
print(list(range(2, 8, 2)))                # [2, 4, 6]

# Filter and map
numbers = [1, 2, 3, 4, 5, 6]
print(list(filter(lambda x: x % 2 == 0, numbers)))  # [2, 4, 6]
print(list(map(lambda x: x**2, numbers)))           # [1, 4, 9, 16, 25, 36]

# Boolean functions
print(all([True, True, True]))     # True
print(all([True, False, True]))    # False
print(any([False, False, True]))   # True
print(any([False, False, False]))  # False
```

### Object Introspection

```python
class Example:
    class_var = "class variable"
    
    def __init__(self):
        self.instance_var = "instance variable"
    
    def method(self):
        pass

obj = Example()

# Object inspection
print(dir(obj))                    # List all attributes
print(vars(obj))                   # Object's __dict__
print(hasattr(obj, 'method'))      # True
print(getattr(obj, 'missing', 'default'))  # 'default'

setattr(obj, 'new_attr', 'new value')
print(obj.new_attr)                # 'new value'

delattr(obj, 'new_attr')
print(hasattr(obj, 'new_attr'))    # False

# Callable checking
print(callable(obj.method))        # True
print(callable(obj.instance_var))  # False

# ID and hash
print(id(obj))                     # Memory address
print(hash("hello"))               # Hash value (for hashable objects)

# Help and documentation
help(len)                          # Interactive help
print(len.__doc__)                 # Docstring
```

### Advanced Built-ins

```python
# exec and eval (use with caution!)
code = "result = 2 + 3"
namespace = {}
exec(code, namespace)
print(namespace['result'])         # 5

expression = "2 + 3 * 4"
result = eval(expression)
print(result)                      # 14

# compile for optimization
code = compile("2 + 3", "<string>", "eval")
result = eval(code)
print(result)                      # 5

# globals and locals
global_var = "I'm global"

def function_scope():
    local_var = "I'm local"
    print(f"Globals: {list(globals().keys())[:5]}")  # First 5 global names
    print(f"Locals: {locals()}")

function_scope()

# Property function (alternative to @property decorator)
class Circle:
    def __init__(self, radius):
        self._radius = radius
    
    def get_area(self):
        return 3.14159 * self._radius ** 2
    
    def set_radius(self, value):
        if value < 0:
            raise ValueError("Radius must be positive")
        self._radius = value
    
    def get_radius(self):
        return self._radius
    
    area = property(get_area)
    radius = property(get_radius, set_radius)

circle = Circle(5)
print(circle.area)                 # 78.53975
circle.radius = 10
print(circle.area)                 # 314.159

# super() function
class A:
    def method(self):
        print("A.method")

class B(A):
    def method(self):
        super().method()
        print("B.method")

class C(A):
    def method(self):
        super().method()
        print("C.method")

class D(B, C):
    def method(self):
        super().method()
        print("D.method")

D().method()
# Output: A.method, C.method, B.method, D.method
```

---

## Common Patterns & Best Practices

### Design Patterns

```python
# Singleton Pattern
class Singleton:
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self.value = 0
            self._initialized = True

# Factory Pattern
class Animal:
    def speak(self):
        raise NotImplementedError

class Dog(Animal):
    def speak(self):
        return "Woof!"

class Cat(Animal):
    def speak(self):
        return "Meow!"

class AnimalFactory:
    @staticmethod
    def create_animal(animal_type):
        if animal_type == "dog":
            return Dog()
        elif animal_type == "cat":
            return Cat()
        else:
            raise ValueError(f"Unknown animal type: {animal_type}")

# Observer Pattern
class Subject:
    def __init__(self):
        self._observers = []
        self._state = None
    
    def attach(self, observer):
        self._observers.append(observer)
    
    def detach(self, observer):
        self._observers.remove(observer)
    
    def notify(self):
        for observer in self._observers:
            observer.update(self._state)
    
    def set_state(self, state):
        self._state = state
        self.notify()

class Observer:
    def __init__(self, name):
        self.name = name
    
    def update(self, state):
        print(f"{self.name} received update: {state}")

# Strategy Pattern
class SortStrategy:
    def sort(self, data):
        raise NotImplementedError

class BubbleSort(SortStrategy):
    def sort(self, data):
        # Simplified bubble sort
        n = len(data)
        for i in range(n):
            for j in range(0, n - i - 1):
                if data[j] > data[j + 1]:
                    data[j], data[j + 1] = data[j + 1], data[j]
        return data

class QuickSort(SortStrategy):
    def sort(self, data):
        if len(data) <= 1:
            return data
        pivot = data[len(data) // 2]
        left = [x for x in data if x < pivot]
        middle = [x for x in data if x == pivot]
        right = [x for x in data if x > pivot]
        return self.sort(left) + middle + self.sort(right)

class Sorter:
    def __init__(self, strategy):
        self.strategy = strategy
    
    def sort(self, data):
        return self.strategy.sort(data.copy())
```

### Error Handling Patterns

```python
# EAFP (Easier to Ask for Forgiveness than Permission)
def eafp_example(dictionary, key):
    try:
        return dictionary[key]
    except KeyError:
        return None

# LBYL (Look Before You Leap)
def lbyl_example(dictionary, key):
    if key in dictionary:
        return dictionary[key]
    return None

# Context manager for error handling
from contextlib import contextmanager

@contextmanager
def error_handler(error_type, default_value=None):
    try:
        yield
    except error_type:
        return default_value

# Resource management patterns
class ResourceManager:
    def __init__(self, resource_name):
        self.resource_name = resource_name
        self.resource = None
    
    def __enter__(self):
        print(f"Acquiring {self.resource_name}")
        self.resource = f"Resource: {self.resource_name}"
        return self.resource
    
    def __exit__(self, exc_type, exc_value, traceback):
        print(f"Releasing {self.resource_name}")
        self.resource = None
        if exc_type:
            print(f"Exception during resource usage: {exc_type.__name__}")
        return False

# Retry pattern
import time
import random
from functools import wraps

def retry(max_attempts=3, delay=1, backoff=2):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            attempts = 0
            current_delay = delay
            
            while attempts < max_attempts:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    attempts += 1
                    if attempts == max_attempts:
                        raise
                    
                    print(f"Attempt {attempts} failed: {e}")
                    time.sleep(current_delay)
                    current_delay *= backoff
            
        return wrapper
    return decorator

@retry(max_attempts=3, delay=0.5)
def unreliable_function():
    if random.random() < 0.7:
        raise ConnectionError("Network error")
    return "Success!"
```

### Performance Patterns

```python
from functools import lru_cache, partial
import time

# Memoization
@lru_cache(maxsize=128)
def expensive_function(n):
    time.sleep(0.1)  # Simulate expensive computation
    return n * n

# Cache info
print(expensive_function(5))
print(expensive_function.cache_info())

# Lazy evaluation
class LazyProperty:
    def __init__(self, func):
        self.func = func
        self.name = func.__name__
    
    def __get__(self, instance, owner):
        if instance is None:
            return self
        
        # Calculate value and cache it
        value = self.func(instance)
        setattr(instance, self.name, value)
        return value

class DataProcessor:
    def __init__(self, data):
        self.data = data
    
    @LazyProperty
    def processed_data(self):
        print("Processing data...")  # Only runs once
        return [x * 2 for x in self.data]

# Generator for memory efficiency
def process_large_file(filename):
    with open(filename, 'r') as file:
        for line in file:
            yield line.strip().upper()

# Partial application for optimization
def multiply(x, y, z):
    return x * y * z

double = partial(multiply, 2)  # Fix first argument
numbers = [1, 2, 3, 4, 5]
doubled = [double(n, 1) for n in numbers]

# Slots for memory optimization
class Point:
    __slots__ = ['x', 'y']
    
    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    def distance_from_origin(self):
        return (self.x ** 2 + self.y ** 2) ** 0.5
```

### Code Organization Patterns

```python
# Module-level constants
DEFAULT_TIMEOUT = 30
MAX_RETRIES = 3
API_VERSION = "v1"

# Configuration class
class Config:
    DEBUG = False
    DATABASE_URL = "sqlite:///app.db"
    SECRET_KEY = "your-secret-key"
    
    @classmethod
    def from_dict(cls, config_dict):
        for key, value in config_dict.items():
            if hasattr(cls, key):
                setattr(cls, key, value)

# Abstract base classes
from abc import ABC, abstractmethod

class DataProcessor(ABC):
    @abstractmethod
    def process(self, data):
        pass
    
    @abstractmethod
    def validate(self, data):
        pass
    
    def run(self, data):
        if self.validate(data):
            return self.process(data)
        raise ValueError("Invalid data")

class CSVProcessor(DataProcessor):
    def validate(self, data):
        return isinstance(data, str) and ',' in data
    
    def process(self, data):
        return data.split(',')

# Namespace pattern
class Constants:
    class HTTP:
        OK = 200
        NOT_FOUND = 404
        SERVER_ERROR = 500
    
    class Database:
        TIMEOUT = 30
        MAX_CONNECTIONS = 100

# Factory registry pattern
class ProcessorRegistry:
    _processors = {}
    
    @classmethod
    def register(cls, name):
        def decorator(processor_class):
            cls._processors[name] = processor_class
            return processor_class
        return decorator
    
    @classmethod
    def create(cls, name, *args, **kwargs):
        if name not in cls._processors:
            raise ValueError(f"Unknown processor: {name}")
        return cls._processors[name](*args, **kwargs)

@ProcessorRegistry.register('csv')
class CSVProcessor:
    def __init__(self, delimiter=','):
        self.delimiter = delimiter

@ProcessorRegistry.register('json')
class JSONProcessor:
    def __init__(self, indent=None):
        self.indent = indent

# Usage
csv_processor = ProcessorRegistry.create('csv', delimiter=';')
json_processor = ProcessorRegistry.create('json', indent=2)
```

---

## Dataclasses and Modern Class Patterns

### Dataclasses

```python
from dataclasses import dataclass, field, asdict, astuple, fields
from typing import List, Optional, ClassVar
import json

@dataclass
class Person:
    name: str
    age: int
    email: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    _id: int = field(init=False, repr=False)
    
    # Class variable (not an instance field)
    species: ClassVar[str] = "Homo sapiens"
    
    def __post_init__(self):
        # Called after __init__
        self._id = hash(self.name)
        if self.age < 0:
            raise ValueError("Age must be positive")

# Usage
person = Person("Alice", 30, "alice@example.com", ["developer", "python"])
print(person)  # Person(name='Alice', age=30, email='alice@example.com', tags=['developer', 'python'])

# Convert to dict/tuple
print(asdict(person))
print(astuple(person))

# Field introspection
for field_info in fields(person):
    print(f"{field_info.name}: {field_info.type} = {getattr(person, field_info.name)}")

# Dataclass options
@dataclass(frozen=True, order=True)  # Immutable and comparable
class Point:
    x: float
    y: float
    
    def distance_from_origin(self) -> float:
        return (self.x ** 2 + self.y ** 2) ** 0.5

points = [Point(3, 4), Point(1, 2), Point(5, 0)]
print(sorted(points))  # Sorted by (x, y) tuples

# Advanced field options
@dataclass
class ConfiguredClass:
    # Field with validation
    name: str = field(metadata={'required': True})
    
    # Computed field
    computed: str = field(init=False)
    
    # Private field
    _internal: int = field(default=0, repr=False, compare=False)
    
    # Field with custom comparison
    priority: int = field(default=1, compare=True)
    
    def __post_init__(self):
        self.computed = f"Computed: {self.name}"

# Inheritance with dataclasses
@dataclass
class Animal:
    name: str
    species: str

@dataclass
class Dog(Animal):
    breed: str
    species: str = "Canis lupus"  # Override default

dog = Dog("Buddy", "Golden Retriever")
print(dog)  # Dog(name='Buddy', species='Canis lupus', breed='Golden Retriever')
```


---

## Type Hints and Typing System

### Basic Type Hints

```python
from typing import (
    List, Dict, Set, Tuple, Optional, Union, Any, Callable,
    TypeVar, Generic, Protocol, Final, Literal, overload
)
from typing_extensions import TypedDict, NotRequired
import sys

# Basic type annotations
def greet(name: str, age: int) -> str:
    return f"Hello {name}, you are {age} years old"

# Collection types
def process_data(
    items: List[str],
    mapping: Dict[str, int],
    unique_values: Set[float],
    coordinates: Tuple[float, float]
) -> Optional[str]:
    if not items:
        return None
    return f"Processed {len(items)} items"

# Union types
def handle_input(value: Union[str, int, float]) -> str:
    return str(value)

# Python 3.10+ union syntax
if sys.version_info >= (3, 10):
    def new_union(value: str | int | float) -> str:
        return str(value)

# Callable types
def apply_function(func: Callable[[int, int], int], a: int, b: int) -> int:
    return func(a, b)

def add(x: int, y: int) -> int:
    return x + y

result = apply_function(add, 5, 3)

# Generic types
T = TypeVar('T')
U = TypeVar('U')

def first(items: List[T]) -> Optional[T]:
    return items[0] if items else None

def map_values(mapping: Dict[str, T], func: Callable[[T], U]) -> Dict[str, U]:
    return {k: func(v) for k, v in mapping.items()}

# Generic classes
class Stack(Generic[T]):
    def __init__(self) -> None:
        self._items: List[T] = []
    
    def push(self, item: T) -> None:
        self._items.append(item)
    
    def pop(self) -> T:
        return self._items.pop()
    
    def is_empty(self) -> bool:
        return len(self._items) == 0

# Usage
int_stack: Stack[int] = Stack()
int_stack.push(42)

str_stack: Stack[str] = Stack()
str_stack.push("hello")
```

### Advanced Type Patterns

```python
# Literal types
from typing import Literal

def set_mode(mode: Literal["read", "write", "append"]) -> None:
    print(f"Mode set to: {mode}")

# Final types
from typing import Final

MAX_SIZE: Final = 1000
# MAX_SIZE = 2000  # Type checker would warn

# TypedDict
class PersonDict(TypedDict):
    name: str
    age: int
    email: NotRequired[str]  # Optional field

def process_person(person: PersonDict) -> str:
    return f"{person['name']} is {person['age']} years old"

# Overloaded functions
@overload
def process(value: str) -> str: ...

@overload
def process(value: int) -> int: ...

def process(value: Union[str, int]) -> Union[str, int]:
    if isinstance(value, str):
        return value.upper()
    return value * 2

# Type aliases
UserID = int
Username = str
UserData = Dict[UserID, Username]

# NewType for distinct types
from typing import NewType

UserId = NewType('UserId', int)
ProductId = NewType('ProductId', int)

def get_user(user_id: UserId) -> str:
    return f"User {user_id}"

# Type checking
if sys.version_info >= (3, 8):
    from typing import TYPE_CHECKING
    
    if TYPE_CHECKING:
        # Only imported during type checking
        from expensive_module import ExpensiveClass
    
    def use_expensive(obj: 'ExpensiveClass') -> None:
        pass
```

### Protocols (Structural Subtyping)

```python
from typing import Protocol, runtime_checkable

class Drawable(Protocol):
    def draw(self) -> None: ...

class Movable(Protocol):
    def move(self, dx: float, dy: float) -> None: ...

# Classes that satisfy protocols without explicit inheritance
class Circle:
    def draw(self) -> None:
        print("Drawing circle")
    
    def move(self, dx: float, dy: float) -> None:
        print(f"Moving circle by ({dx}, {dy})")

class Rectangle:
    def draw(self) -> None:
        print("Drawing rectangle")

# Function that works with any drawable object
def render(obj: Drawable) -> None:
    obj.draw()

# Works with both Circle and Rectangle
render(Circle())
render(Rectangle())

# Runtime checkable protocols
@runtime_checkable
class Sized(Protocol):
    def __len__(self) -> int: ...

# Check at runtime
print(isinstance([], Sized))    # True
print(isinstance("hello", Sized))  # True
print(isinstance(42, Sized))    # False

# Complex protocol example
class SupportsWrite(Protocol):
    def write(self, data: str) -> int: ...

def save_data(file: SupportsWrite, data: str) -> None:
    file.write(data)

# Works with any object that has a write method
import io
save_data(io.StringIO(), "Hello")
```

---

## Enum Classes

### Basic Enums

```python
from enum import Enum, IntEnum, Flag, IntFlag, auto
from typing import Union

# Basic enum
class Color(Enum):
    RED = 1
    GREEN = 2
    BLUE = 3

print(Color.RED)           # Color.RED
print(Color.RED.name)      # 'RED'
print(Color.RED.value)     # 1
print(repr(Color.RED))     # <Color.RED: 1>

# Iteration
for color in Color:
    print(f"{color.name}: {color.value}")

# Comparison
print(Color.RED == Color.RED)    # True
print(Color.RED == Color.BLUE)   # False
print(Color.RED is Color.RED)    # True

# Functional API
Direction = Enum('Direction', 'NORTH SOUTH EAST WEST')
print(list(Direction))

# Auto values
class Planet(Enum):
    MERCURY = auto()
    VENUS = auto()
    EARTH = auto()
    MARS = auto()

print(Planet.EARTH.value)  # 3

# String enums
class Status(Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    
    def __str__(self):
        return self.value

print(Status.PENDING)      # Status.PENDING
print(str(Status.PENDING)) # pending

# Enum with methods
class Planet(Enum):
    MERCURY = (3.303e+23, 2.4397e6)
    VENUS   = (4.869e+24, 6.0518e6)
    EARTH   = (5.976e+24, 6.37814e6)
    MARS    = (6.421e+23, 3.3972e6)
    
    def __init__(self, mass, radius):
        self.mass = mass       # in kilograms
        self.radius = radius   # in meters
    
    @property
    def surface_gravity(self):
        G = 6.67300E-11
        return G * self.mass / (self.radius * self.radius)

print(Planet.EARTH.surface_gravity)  # 9.802652743337129
```

### Advanced Enum Patterns

```python
# IntEnum - can be compared with integers
class Priority(IntEnum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4

print(Priority.HIGH > Priority.LOW)  # True
print(Priority.HIGH > 2)             # True

# Flag enum for bitwise operations
class Permission(Flag):
    READ = auto()
    WRITE = auto()
    EXECUTE = auto()

# Combine permissions
rw = Permission.READ | Permission.WRITE
print(rw)  # Permission.WRITE|READ

# Check permissions
print(Permission.READ in rw)    # True
print(Permission.EXECUTE in rw) # False

# IntFlag combines Flag and IntEnum
class FileMode(IntFlag):
    R = 4
    W = 2
    X = 1

mode = FileMode.R | FileMode.W
print(int(mode))  # 6

# Unique decorator
from enum import unique

@unique
class Color(Enum):
    RED = 1
    GREEN = 2
    BLUE = 3
    # CRIMSON = 1  # Would raise ValueError due to @unique

# Functional enum with complex values
HttpStatus = Enum('HttpStatus', {
    'OK': (200, 'OK'),
    'NOT_FOUND': (404, 'Not Found'),
    'SERVER_ERROR': (500, 'Internal Server Error')
})

# Custom enum base class
class BaseEnum(Enum):
    def __str__(self):
        return self.name.lower()
    
    @classmethod
    def choices(cls):
        return [(member.value, member.name) for member in cls]

class Priority(BaseEnum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3

print(Priority.choices())  # [(1, 'LOW'), (2, 'MEDIUM'), (3, 'HIGH')]
```

---

## NamedTuple and TypedDict

### NamedTuple

```python
from typing import NamedTuple
from collections import namedtuple

# Old style namedtuple
Point = namedtuple('Point', ['x', 'y'])
p1 = Point(1, 2)
print(p1.x, p1.y)  # 1 2

# New style with typing
class Point(NamedTuple):
    x: float
    y: float
    
    def distance_from_origin(self) -> float:
        return (self.x ** 2 + self.y ** 2) ** 0.5

p2 = Point(3.0, 4.0)
print(p2.distance_from_origin())  # 5.0

# NamedTuple with default values
class Person(NamedTuple):
    name: str
    age: int
    city: str = "Unknown"

person = Person("Alice", 30)
print(person)  # Person(name='Alice', age=30, city='Unknown')

# NamedTuple methods
print(person._asdict())      # {'name': 'Alice', 'age': 30, 'city': 'Unknown'}
print(person._replace(age=31))  # Person(name='Alice', age=31, city='Unknown')

# Subclassing NamedTuple
class Employee(NamedTuple):
    name: str
    employee_id: int
    department: str
    
    @property
    def email(self) -> str:
        return f"{self.name.lower()}@company.com"
    
    def __str__(self) -> str:
        return f"{self.name} ({self.employee_id})"

emp = Employee("Alice Johnson", 12345, "Engineering")
print(emp.email)  # alice johnson@company.com

# Generic NamedTuple
from typing import TypeVar, Generic

T = TypeVar('T')

class Pair(NamedTuple, Generic[T]):
    first: T
    second: T

int_pair = Pair(1, 2)
str_pair = Pair("hello", "world")
```

### TypedDict

```python
from typing_extensions import TypedDict, Required, NotRequired
from typing import Union

# Basic TypedDict
class Person(TypedDict):
    name: str
    age: int
    email: str

def greet_person(person: Person) -> str:
    return f"Hello {person['name']}, age {person['age']}"

person_data: Person = {
    "name": "Alice",
    "age": 30,
    "email": "alice@example.com"
}

# TypedDict with optional fields (Python 3.11+)
class PersonOptional(TypedDict):
    name: Required[str]
    age: Required[int]
    email: NotRequired[str]

# Pre-3.11 syntax for optional fields
class PersonTotal(TypedDict, total=False):
    name: str  # Optional
    age: str   # Optional

class PersonMixed(PersonTotal):
    id: str    # Required (inherits total=False but can override)

# Functional syntax
Person = TypedDict('Person', {
    'name': str,
    'age': int,
    'email': str
})

# Inheritance
class Employee(Person):
    employee_id: str
    department: str

# Generic TypedDict
from typing import TypeVar

T = TypeVar('T')

class Container(TypedDict, Generic[T]):
    data: T
    metadata: dict[str, str]

# Union with TypedDict
UserData = Union[Person, Employee]

def process_user(user: UserData) -> str:
    if 'employee_id' in user:
        # Type narrowing
        return f"Employee: {user['name']}"
    else:
        return f"Person: {user['name']}"
```

---

## Collections Module Deep Dive

### Specialized Data Structures

```python
from collections import (
    defaultdict, Counter, deque, ChainMap, OrderedDict,
    UserDict, UserList, UserString, namedtuple
)

# defaultdict - never raises KeyError
dd = defaultdict(list)
dd['fruits'].append('apple')
dd['fruits'].append('banana')
print(dd)  # defaultdict(<class 'list'>, {'fruits': ['apple', 'banana']})

# defaultdict with lambda
dd_int = defaultdict(lambda: 0)
dd_int['count'] += 1
print(dd_int['count'])  # 1

# Counter - count hashable objects
text = "hello world"
counter = Counter(text)
print(counter)  # Counter({'l': 3, 'o': 2, 'h': 1, 'e': 1, ' ': 1, 'w': 1, 'r': 1, 'd': 1})

# Counter methods
print(counter.most_common(3))  # [('l', 3), ('o', 2), ('h', 1)]
print(counter.total())         # 11
print(counter.elements())      # Iterator over elements

# Counter arithmetic
c1 = Counter(['a', 'b', 'c', 'a'])
c2 = Counter(['a', 'b', 'b', 'd'])
print(c1 + c2)  # Counter({'a': 3, 'b': 3, 'c': 1, 'd': 1})
print(c1 - c2)  # Counter({'c': 1, 'a': 1})
print(c1 & c2)  # Counter({'a': 1, 'b': 1}) - intersection
print(c1 | c2)  # Counter({'a': 2, 'b': 2, 'c': 1, 'd': 1}) - union

# deque - double-ended queue
dq = deque([1, 2, 3], maxlen=5)
dq.appendleft(0)    # deque([0, 1, 2, 3])
dq.append(4)        # deque([0, 1, 2, 3, 4])
dq.append(5)        # deque([1, 2, 3, 4, 5]) - 0 was dropped

# deque methods
dq.rotate(2)        # deque([4, 5, 1, 2, 3])
dq.extendleft([10, 11])  # deque([11, 10, 4, 5, 1])

# ChainMap - combine multiple mappings
dict1 = {'a': 1, 'b': 2}
dict2 = {'b': 3, 'c': 4}
dict3 = {'c': 5, 'd': 6}

cm = ChainMap(dict1, dict2, dict3)
print(cm['a'])  # 1 (from dict1)
print(cm['b'])  # 2 (from dict1, first mapping wins)
print(cm['c'])  # 4 (from dict2)

# ChainMap methods
print(cm.maps)     # [{'a': 1, 'b': 2}, {'b': 3, 'c': 4}, {'c': 5, 'd': 6}]
cm2 = cm.new_child({'x': 99})  # Add new mapping at front

# OrderedDict (less relevant in Python 3.7+ where dict is ordered)
od = OrderedDict([('a', 1), ('b', 2), ('c', 3)])
od.move_to_end('a')  # Move 'a' to end
print(od)  # OrderedDict([('b', 2), ('c', 3), ('a', 1)])

od.popitem(last=False)  # Remove first item
print(od)  # OrderedDict([('c', 3), ('a', 1)])
```

### User Classes for Subclassing

```python
# UserDict - for creating dict-like classes
class UpperDict(UserDict):
    def __setitem__(self, key, value):
        # Convert all keys to uppercase
        super().__setitem__(key.upper(), value)
    
    def __getitem__(self, key):
        return super().__getitem__(key.upper())

ud = UpperDict()
ud['hello'] = 'world'
print(ud['HELLO'])  # world
print(ud.data)      # {'HELLO': 'world'}

# UserList - for creating list-like classes
class LoggingList(UserList):
    def append(self, item):
        print(f"Appending {item}")
        super().append(item)
    
    def __setitem__(self, index, value):
        print(f"Setting index {index} to {value}")
        super().__setitem__(index, value)

ll = LoggingList([1, 2, 3])
ll.append(4)      # Appending 4
ll[0] = 99        # Setting index 0 to 99

# UserString - for creating string-like classes
class ReversibleString(UserString):
    def reverse(self):
        return self.__class__(self.data[::-1])
    
    def __add__(self, other):
        if isinstance(other, UserString):
            return self.__class__(self.data + other.data)
        return self.__class__(self.data + str(other))

rs = ReversibleString("hello")
print(rs.reverse())      # olleh
print(rs + " world")     # hello world
```

---

## Functools Module Deep Dive

### Function Utilities

```python
from functools import (
    partial, lru_cache, singledispatch, wraps, reduce,
    cached_property, total_ordering, update_wrapper
)
import operator

# partial - freeze function arguments
def multiply(x, y, z):
    return x * y * z

double = partial(multiply, 2)      # Fix first argument
print(double(3, 4))  # 24 (2 * 3 * 4)

# partial with keyword arguments
def greet(greeting, name, punctuation="!"):
    return f"{greeting} {name}{punctuation}"

say_hello = partial(greet, "Hello", punctuation=".")
print(say_hello("Alice"))  # Hello Alice.

# lru_cache - memoization
@lru_cache(maxsize=128)
def fibonacci(n):
    if n < 2:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

print(fibonacci(50))
print(fibonacci.cache_info())  # CacheInfo(hits=48, misses=51, maxsize=128, currsize=51)

# Clear cache
fibonacci.cache_clear()

# singledispatch - function overloading based on type
@singledispatch
def process(arg):
    print(f"Processing {type(arg).__name__}: {arg}")

@process.register
def _(arg: int):
    print(f"Processing integer: {arg * 2}")

@process.register
def _(arg: str):
    print(f"Processing string: {arg.upper()}")

@process.register
def _(arg: list):
    print(f"Processing list of {len(arg)} items")

process(42)        # Processing integer: 84
process("hello")   # Processing string: HELLO
process([1, 2, 3]) # Processing list of 3 items

# wraps - preserve function metadata
def logged(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        print(f"Calling {func.__name__}")
        return func(*args, **kwargs)
    return wrapper

@logged
def example():
    """This is an example function."""
    return "result"

print(example.__name__)  # example (not wrapper)
print(example.__doc__)   # This is an example function.

# cached_property - property with caching
class DataProcessor:
    def __init__(self, data):
        self.data = data
    
    @cached_property
    def processed_data(self):
        print("Processing data...")  # Only called once
        return [x * 2 for x in self.data]

dp = DataProcessor([1, 2, 3, 4, 5])
print(dp.processed_data)  # Processing data... [2, 4, 6, 8, 10]
print(dp.processed_data)  # [2, 4, 6, 8, 10] (cached)

# total_ordering - complete ordering from minimal methods
@total_ordering
class Grade:
    def __init__(self, score):
        self.score = score
    
    def __eq__(self, other):
        return self.score == other.score
    
    def __lt__(self, other):
        return self.score < other.score
    
    # __le__, __gt__, __ge__ are automatically generated

grades = [Grade(85), Grade(92), Grade(78)]
print(sorted(grades, key=lambda g: g.score))

# reduce - apply function cumulatively
numbers = [1, 2, 3, 4, 5]
product = reduce(operator.mul, numbers)  # 1*2*3*4*5 = 120
print(product)

# reduce with initial value
total = reduce(operator.add, numbers, 100)  # 100+1+2+3+4+5 = 115
print(total)
```

### Advanced Functools Patterns

```python
# Generic function dispatch
from functools import singledispatchmethod

class Formatter:
    @singledispatchmethod
    def format(self, arg):
        return str(arg)
    
    @format.register
    def _(self, arg: int):
        return f"Integer: {arg:,}"
    
    @format.register
    def _(self, arg: float):
        return f"Float: {arg:.2f}"
    
    @format.register
    def _(self, arg: bool):
        return f"Boolean: {'Yes' if arg else 'No'}"

formatter = Formatter()
print(formatter.format(1000))     # Integer: 1,000
print(formatter.format(3.14159))  # Float: 3.14
print(formatter.format(True))     # Boolean: Yes

# Custom cache implementation
def custom_cache(maxsize=128):
    def decorator(func):
        cache = {}
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            key = str(args) + str(sorted(kwargs.items()))
            if key not in cache:
                if len(cache) >= maxsize:
                    # Simple FIFO eviction
                    oldest_key = next(iter(cache))
                    del cache[oldest_key]
                cache[key] = func(*args, **kwargs)
            return cache[key]
        
        wrapper.cache_clear = lambda: cache.clear()
        wrapper.cache_info = lambda: f"Cache size: {len(cache)}"
        
        return wrapper
    return decorator

@custom_cache(maxsize=3)
def expensive_function(n):
    print(f"Computing {n}")
    return n ** 2

# Composition with functools
def compose(*functions):
    return reduce(lambda f, g: lambda x: f(g(x)), functions, lambda x: x)

# Example: create a pipeline
add_one = lambda x: x + 1
multiply_by_two = lambda x: x * 2
square = lambda x: x ** 2

pipeline = compose(square, multiply_by_two, add_one)
print(pipeline(3))  # ((3 + 1) * 2) ** 2 = 64
```

---

## Pathlib - Modern Path Handling

### Basic Path Operations

```python
from pathlib import Path, PurePath
import os

# Create path objects
p = Path('/home/user/documents/file.txt')
current = Path.cwd()  # Current working directory
home = Path.home()    # User home directory

print(f"Current directory: {current}")
print(f"Home directory: {home}")

# Path components
print(f"Parent: {p.parent}")           # /home/user/documents
print(f"Name: {p.name}")               # file.txt
print(f"Stem: {p.stem}")               # file
print(f"Suffix: {p.suffix}")           # .txt
print(f"Parts: {p.parts}")             # ('/', 'home', 'user', 'documents', 'file.txt')

# Path operations
new_path = p.with_name('new_file.txt')
print(new_path)  # /home/user/documents/new_file.txt

new_ext = p.with_suffix('.md')
print(new_ext)   # /home/user/documents/file.md

# Joining paths
base = Path('/home/user')
full_path = base / 'documents' / 'file.txt'
print(full_path)  # /home/user/documents/file.txt

# Path resolution
relative = Path('.')
absolute = relative.resolve()
print(f"Resolved: {absolute}")

# Path matching
pattern_path = Path('/home/user/docs/file.txt')
print(pattern_path.match('*.txt'))      # True
print(pattern_path.match('*/docs/*'))   # True
print(pattern_path.match('**/file.txt')) # True
```

### File System Operations

```python
# File/directory operations
test_dir = Path('test_directory')
test_file = test_dir / 'test_file.txt'

# Create directory
test_dir.mkdir(exist_ok=True, parents=True)
print(f"Directory exists: {test_dir.exists()}")
print(f"Is directory: {test_dir.is_dir()}")

# Create file
test_file.write_text('Hello, World!')
print(f"File exists: {test_file.exists()}")
print(f"Is file: {test_file.is_file()}")

# Read file
content = test_file.read_text()
print(f"Content: {content}")

# File statistics
stat = test_file.stat()
print(f"Size: {stat.st_size} bytes")
print(f"Modified: {stat.st_mtime}")

# Binary operations
binary_data = b'Binary content'
test_file.write_bytes(binary_data)
read_binary = test_file.read_bytes()
print(f"Binary data: {read_binary}")

# Iterating over directories
for item in test_dir.iterdir():
    print(f"Item: {item.name}, Type: {'dir' if item.is_dir() else 'file'}")

# Glob patterns
python_files = list(Path('.').glob('*.py'))
print(f"Python files: {[f.name for f in python_files]}")

# Recursive glob
all_python = list(Path('.').rglob('*.py'))
print