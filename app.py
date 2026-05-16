import argparse
import logging
from typing import Optional

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

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

def main() -> None:
    """Main execution entry point."""
    parser = argparse.ArgumentParser(description="A sample CLI application offering greeting and math functionalities.")

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Subparser for greeting
    parser_greet = subparsers.add_parser('greet', help='Greet a user')
    parser_greet.add_argument('--name', type=str, required=True, help="Name of the person to greet")

    # Subparser for addition
    parser_add = subparsers.add_parser('add', help='Add two numbers together')
    parser_add.add_argument('--a', type=float, required=True, help="First number")
    parser_add.add_argument('--b', type=float, required=True, help="Second number")

    args = parser.parse_args()

    if args.command == 'greet':
        try:
            message = greet(args.name)
            logging.info(message)
        except ValueError as e:
            logging.error(f"Error generating greeting: {e}")

    elif args.command == 'add':
        result = add_numbers(args.a, args.b)
        logging.info(f"The result of adding {args.a} and {args.b} is: {result}")

    else:
        parser.print_help()

if __name__ == "__main__":
    main()
