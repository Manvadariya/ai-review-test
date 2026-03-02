import re
from typing import List, Tuple

def check_sql_injection_vulnerability(query: str) -> bool:
    """Check if query is vulnerable to SQL injection."""
    dangerous_patterns = [
        r"'\s*OR\s*'",
        r"'\s*AND\s*'",
        r"--\s*$",
        r";.*DELETE",
        r";.*DROP"
    ]
    return any(re.search(pattern, query, re.IGNORECASE) for pattern in dangerous_patterns)

def check_hardcoded_credentials(code: str) -> List[str]:
    """Detect hardcoded passwords or API keys."""
    patterns = [
        r"password\s*=\s*['\"].*['\"]",
        r"api_key\s*=\s*['\"].*['\"]",
        r"secret\s*=\s*['\"].*['\"]"
    ]
    vulnerabilities = []
    for pattern in patterns:
        if re.search(pattern, code, re.IGNORECASE):
            vulnerabilities.append(f"Found hardcoded credential pattern: {pattern}")
    return vulnerabilities

def check_input_validation(user_input: str) -> Tuple[bool, str]:
    """Check if user input is properly validated."""
    if not user_input or not isinstance(user_input, str):
        return False, "Input not validated"
    if len(user_input) > 1000:
        return False, "Input exceeds safe length"
    return True, "Input is safe"

# Example usage
if __name__ == "__main__":
    vulnerable_query = "SELECT * FROM users WHERE id=1 OR '1'='1'"
    print(f"SQL Injection vulnerable: {check_sql_injection_vulnerability(vulnerable_query)}")
    
    safe_input, msg = check_input_validation("test_input")
    print(f"Input validation: {safe_input} - {msg}")