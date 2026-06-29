import math
import secrets
import string
import functools
from typing import List, Dict, Any

def greet(name: str) -> str:
    """Returns a greeting message."""
    if not name:
        raise ValueError("Name cannot be empty")
    return f"Hello, {name}!"

# --- Math Operations ---

def add_numbers(a: float, b: float) -> float:
    """Adds two numbers and returns the result."""
    return a + b

def subtract(a: float, b: float) -> float:
    """Subtracts b from a."""
    return a - b

def multiply(a: float, b: float) -> float:
    """Multiplies two numbers."""
    return a * b

def divide(a: float, b: float) -> float:
    """Divides a by b."""
    if b == 0:
        raise ValueError("Division by zero is not allowed.")
    return a / b

def power(a: float, b: float) -> float:
    """Raises a to the power of b."""
    # Add bounds to avoid huge computations DoS
    if a > 10000 or b > 10000:
        raise ValueError("Inputs too large for power operation.")
    try:
        return math.pow(a, b)
    except OverflowError:
        raise ValueError("Result too large.")

def sqrt(a: float) -> float:
    """Returns the square root of a."""
    if a < 0:
        raise ValueError("Cannot calculate square root of a negative number.")
    return math.sqrt(a)

@functools.lru_cache(maxsize=128)
def factorial(n: int) -> int:
    """Returns the factorial of a positive integer."""
    if n < 0:
        raise ValueError("Factorial is not defined for negative numbers.")
    if n > 1000:
        raise ValueError("Number too large for factorial computation.")
    return math.factorial(n)

def statistics_mean(numbers: List[float]) -> float:
    """Calculates the mean of a list of numbers."""
    if not numbers:
        raise ValueError("List cannot be empty.")
    return sum(numbers) / len(numbers)

def statistics_variance(numbers: List[float]) -> float:
    """Calculates the variance of a list of numbers."""
    if not numbers:
        raise ValueError("List cannot be empty.")
    if len(numbers) < 2:
        return 0.0
    m = statistics_mean(numbers)
    return sum((x - m) ** 2 for x in numbers) / len(numbers)

# --- Text Operations ---

def analyze_text(text: str) -> Dict[str, Any]:
    """Provides statistical analysis of a given text."""
    if text is None:
        raise ValueError("Text cannot be None.")
    words = text.split()
    return {
        "char_count": len(text),
        "word_count": len(words),
        "is_palindrome": text == text[::-1] and len(text) > 0,
        "alphanumeric_count": sum(c.isalnum() for c in text)
    }

def transform_text(text: str, operation: str) -> str:
    """Transforms text based on operation."""
    if text is None:
        raise ValueError("Text cannot be None.")
    if operation == "uppercase":
        return text.upper()
    elif operation == "lowercase":
        return text.lower()
    elif operation == "reverse":
        return text[::-1]
    else:
        raise ValueError(f"Unknown operation: {operation}")

# --- Utilities ---

def generate_random_string(length: int = 16) -> str:
    """Generates a secure random alphanumeric string."""
    if length <= 0 or length > 1024:
        raise ValueError("Length must be between 1 and 1024.")
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))
