def greet(name: str) -> str:
    """Returns a greeting message.

    Args:
        name (str): The name to greet.

    Returns:
        str: The formatted greeting string.
    """
    if not name:
        raise ValueError("Name cannot be empty")
    return f"Hello, {name}!"

def add_numbers(a: float, b: float) -> float:
    """Adds two numbers and returns the result.

    Args:
        a (float): The first number.
        b (float): The second number.

    Returns:
        float: The sum of the two numbers.
    """
    return a + b
