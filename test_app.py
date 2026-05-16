import unittest
from app import greet, add_numbers

class TestApp(unittest.TestCase):

    def test_greet_valid_name(self):
        """Test greet with a valid string."""
        result = greet("Alice")
        self.assertEqual(result, "Hello, Alice!")

    def test_greet_empty_name(self):
        """Test greet with an empty string raises ValueError."""
        with self.assertRaises(ValueError):
            greet("")

    def test_add_numbers_positive(self):
        """Test adding positive numbers."""
        self.assertEqual(add_numbers(3, 4), 7)

    def test_add_numbers_negative(self):
        """Test adding negative numbers."""
        self.assertEqual(add_numbers(-3, -4), -7)

    def test_add_numbers_mixed(self):
        """Test adding mixed sign numbers."""
        self.assertEqual(add_numbers(5, -2), 3)

    def test_add_numbers_floats(self):
        """Test adding floats."""
        self.assertAlmostEqual(add_numbers(2.5, 3.1), 5.6)

if __name__ == '__main__':
    unittest.main()
