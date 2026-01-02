# Bad Code Example

# Violation: Hardcoded secret (Rule 3)
API_KEY = "12345-secret-key" 

def calculate(x, y):
    # Violation: No docstring explaining WHY (Rule 4)
    return x + y

def get_data():
    # Violation: No error handling (Rule 1)
    data = open("file.txt").read() 
    print(data)

# Violation: Variable naming (Rule 2 - should be snake_case)
myVariable = 10