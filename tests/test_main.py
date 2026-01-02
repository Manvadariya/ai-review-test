import unittest
import os
import sys
from unittest.mock import patch, mock_open
from main import calculate, get_api_key, get_data

class TestMain(unittest.TestCase):
    
    # --- Test calculate ---
    def test_calculate_addition(self):
        """Test simple addition."""
        self.assertEqual(calculate(1, 2), 3)
        self.assertEqual(calculate(0, 0), 0)
        self.assertEqual(calculate(-1, 1), 0)

    # --- Test get_api_key ---
    @patch.dict(os.environ, {"API_KEY": "secret_token"}, clear=True)
    def test_get_api_key_success(self):
        """Test retrieving existing key."""
        self.assertEqual(get_api_key(), "secret_token")

    @patch.dict(os.environ, {}, clear=True)
    def test_get_api_key_missing(self):
        """Test error raised when key is missing."""
        with self.assertRaises(ValueError):
            get_api_key()

    # --- Test get_data ---
    @patch("builtins.open", new_callable=mock_open, read_data="file content")
    def test_get_data_success(self, mock_file):
        """Test reading a valid file."""
        self.assertEqual(get_data("dummy.txt"), "file content")

    @patch("builtins.open", side_effect=FileNotFoundError)
    def test_get_data_not_found(self, mock_file):
        """Test error raised when file is missing."""
        # We expect the function to re-raise FileNotFoundError (based on your code)
        with self.assertRaises(FileNotFoundError):
            get_data("ghost.txt")

if __name__ == '__main__':
    unittest.main()