# Seshat: A Simple Python Function Tracer

Seshat is a lightweight Python module designed for straightforward function tracing. It logs function calls, arguments, keyword arguments, and return values, making it easy to understand the flow of your code.  Seshat also provides a simple proxy class to record READ/WRITE access to object attributes.

## Installation

Seshat is a pure python module.  Just place the `seshat` directory in your project and import it.

## Usage

### Tracing

To trace a function, simply decorate it with `@seshat.record`:

```python
from seshat import seshat

@seshat.record
def my_function(a, b, c):
    result = a + b + c
    return result

my_function(1, 2, 3)
```

This will print the following output to the console:

```plaintext
2024-03-08 10:00:00.000000 [FUNC] [__main__] [ <module> >> my_function() ]
args:
(1, 2, 3)
return:
6
```

Seshat handles keyword arguments and multiple return values. You can decorate nested function calls, generators, even `async` functions.

### Object Proxy

Seshat provides an object proxy to observe all attribute READ and WRITE activity.

```python
from seshat import seshat

class Dog:
	def __init__(self, name):
		self.name = name

	def bark(self):
		print("Woof!")


buddy = Dog("Buddy")

# Create a proxy for the Dog object
buddy = seshat.proxy(buddy)

# Accessing attributes through the proxy will be logged
print(buddy.name)  # Logs the read operation
buddy.name = "Max"  # Logs the write operation
buddy.bark()       # Calls the original bark method (also logged)
```

This will print the following output to the console:

```plaintext
2024-03-08 10:00:00.000000 [READ] [__main__] [ <module> >> buddy.name ]
2024-03-08 10:00:00.000000 [WRITE] [__main__] [ <module> >> buddy.name ]
2024-03-08 10:00:00.000000 [CALL] [__main__] [ <module> >> buddy.bark() ]
```

### Logging Messages

You can add custom log messages using `seshat.info`, `seshat.warn`, and `seshat.error`:

```python
from seshat import seshat

def my_function():
    seshat.info("Starting the function")
    # ... some code ...
    seshat.warn("Something might be wrong")
    # ... more code ...
    seshat.error("An error occurred")

```

Optionally, you can log mesaages to a file by calling `seshat.save_log("seshat.log")` before running your code.