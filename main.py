# Bad Code Example

import os
import logging

logging.basicConfig(level=logging.INFO)

# Violation: Hardcoded secret (Rule 3)
API_KEY = os.getenv('API_KEY') 

def calculate(x, y):
    """Calculate the sum of two numbers.
    
    Args:
        x (int): First number
        y (int): Second number
    
    Returns:
        int: The sum of x and y
    """
    return x + y

def get_data():
    """Read data from file.txt.
    
    Returns:
        str or None: The data from the file, or None if error.
    """
    try:
        with open("file.txt") as f:
            data = f.read()
        return data
    except Exception as e:
        logging.error(f"Error reading file: {e}")
        return None

# Violation: Variable naming (Rule 2 - should be snake_case)
my_variable = 10

if __name__ == "__main__":
    # Unit test for calculate function
    assert calculate(1, 2) == 3
    assert calculate(0, 0) == 0
    assert calculate(-1, 1) == 0
    logging.info("All tests passed")