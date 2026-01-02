import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

# Rule 3: Use environment variables for secrets
API_KEY = os.getenv("API_KEY")

def calculate(x, y):
    """
    Calculate the sum of two numbers.
    
    Args:
        x (int): First number
        y (int): Second number
    
    Returns:
        int: The sum of x and y
    """
    return x + y

def get_data():
    """
    Read data from file.txt safely.
    
    Returns:
        str or None: The file content or None if an error occurs.
    """
    # Rule 1: Error Handling
    try:
        # Rule 2: Using 'with' statement for safe file handling
        with open("file.txt", "r") as f:
            return f.read()
    except FileNotFoundError:
        logging.error("File not found.")
        return None
    except Exception as e:
        logging.error(f"Error reading file: {e}")
        return None

# Rule 2: Naming Conventions (snake_case)
my_variable = 10

if __name__ == "__main__":
    # Rule 6: Basic Unit Tests
    assert calculate(1, 2) == 3
    assert calculate(0, 0) == 0
    assert calculate(-1, 1) == 0
    logging.info("All tests passed.")