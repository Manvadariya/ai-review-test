import unittest
from main import calculate

class TestMain(unittest.TestCase):
    def test_calculate_addition(self):
        """Test that calculate adds numbers correctly."""
        self.assertEqual(calculate(1, 2), 3)
        self.assertEqual(calculate(0, 0), 0)
        self.assertEqual(calculate(-1, 1), 0)

if __name__ == '__main__':
    unittest.main()