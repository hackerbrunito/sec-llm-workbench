"""
Test cases for security-auditor with Chain-of-Thought reasoning.

Purpose: Measure accuracy improvement from CoT prompting.
Expected: +15-25% precision on CRITICAL findings (fewer false positives).
"""

# Test Case 1: SQL Injection (True Positive - CRITICAL)
SQL_INJECTION_CODE = '''
def get_user(user_id: str) -> dict:
    """Fetch user by ID."""
    cursor = db.cursor()
    # VULNERABILITY: Direct string interpolation
    cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")
    return cursor.fetchone()
'''

# Expected CoT reasoning:
# Step 1: Pattern = SQL injection via f-string
# Step 2: Exploitability = HIGH (user controls user_id)
# Step 3: Impact = CRITICAL (full database access)
# Step 4: Severity = CRITICAL
# Step 5: CWE-89 confirmed
EXPECTED_FINDING_1 = {
    "severity": "CRITICAL",
    "cwe": "CWE-89",
    "reasoning_shown": True,
    "false_positive": False
}

# Test Case 2: Parameterized Query (True Negative)
SAFE_SQL_CODE = '''
def get_user(user_id: str) -> dict:
    """Fetch user by ID - SAFE."""
    cursor = db.cursor()
    # SAFE: Parameterized query
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    return cursor.fetchone()
'''

# Expected CoT reasoning:
# Step 1: Pattern = parameterized query
# Step 2: User input properly escaped
# Step 3: No vulnerability
EXPECTED_FINDING_2 = {
    "severity": None,
    "false_positive": False
}

# Test Case 3: Hardcoded Secret (True Positive - CRITICAL)
HARDCODED_SECRET_CODE = '''
import os

class Config:
    # VULNERABILITY: Hardcoded API key
    API_KEY = "sk-1234567890abcdef"
    DATABASE_URL = os.getenv("DATABASE_URL")
'''

# Expected CoT reasoning:
# Step 1: Pattern = hardcoded secret
# Step 2: Exploitability = HIGH (exposed in source)
# Step 3: Impact = CRITICAL (API key compromise)
# Step 4: Severity = CRITICAL
# Step 5: CWE-798 confirmed
EXPECTED_FINDING_3 = {
    "severity": "CRITICAL",
    "cwe": "CWE-798",
    "reasoning_shown": True,
    "false_positive": False
}

# Test Case 4: Environment Variable (True Negative)
SAFE_SECRET_CODE = '''
import os

class Config:
    # SAFE: Environment variable
    API_KEY = os.getenv("API_KEY")
    DATABASE_URL = os.getenv("DATABASE_URL")
'''

EXPECTED_FINDING_4 = {
    "severity": None,
    "false_positive": False
}

# Test Case 5: Command Injection (True Positive - CRITICAL)
COMMAND_INJECTION_CODE = '''
import subprocess

def run_command(user_input: str) -> str:
    # VULNERABILITY: shell=True with user input
    result = subprocess.call(f"echo {user_input}", shell=True)
    return result
'''

EXPECTED_FINDING_5 = {
    "severity": "CRITICAL",
    "cwe": "CWE-78",
    "reasoning_shown": True,
    "false_positive": False
}

# Test Case 6: Safe Subprocess (True Negative)
SAFE_SUBPROCESS_CODE = '''
import subprocess

def run_command(user_input: str) -> str:
    # SAFE: Array form without shell
    result = subprocess.run(["echo", user_input], check=True)
    return result.stdout
'''

EXPECTED_FINDING_6 = {
    "severity": None,
    "false_positive": False
}

# Test Case 7: Pickle Deserialization (True Positive - HIGH)
PICKLE_VULN_CODE = '''
import pickle

def load_data(user_data: bytes) -> dict:
    # VULNERABILITY: Insecure deserialization
    return pickle.loads(user_data)
'''

EXPECTED_FINDING_7 = {
    "severity": "HIGH",
    "cwe": "CWE-502",
    "reasoning_shown": True,
    "false_positive": False
}

# Test Case 8: JSON Deserialization (True Negative)
SAFE_DESERIALIZE_CODE = '''
import json

def load_data(user_data: str) -> dict:
    # SAFE: JSON deserialization
    return json.loads(user_data)
'''

EXPECTED_FINDING_8 = {
    "severity": None,
    "false_positive": False
}

# Test Case 9: Path Traversal (True Positive - HIGH)
PATH_TRAVERSAL_CODE = '''
from pathlib import Path

def read_file(user_path: str) -> str:
    # VULNERABILITY: No path validation
    full_path = Path("/data") / user_path
    return full_path.read_text()
'''

EXPECTED_FINDING_9 = {
    "severity": "HIGH",
    "cwe": "CWE-22",
    "reasoning_shown": True,
    "false_positive": False
}

# Test Case 10: Safe Path Handling (True Negative)
SAFE_PATH_CODE = '''
from pathlib import Path

def read_file(user_path: str, base_dir: Path) -> str:
    # SAFE: Path validation
    safe_path = (base_dir / Path(user_path).name).resolve()
    if not safe_path.is_relative_to(base_dir):
        raise ValueError("Path traversal attempt")
    return safe_path.read_text()
'''

EXPECTED_FINDING_10 = {
    "severity": None,
    "false_positive": False
}

# Test Case 11: Weak Hashing (True Positive - MEDIUM, edge case)
WEAK_HASH_CODE = '''
import hashlib

def hash_password(password: str) -> str:
    # VULNERABILITY: MD5 for password hashing
    return hashlib.md5(password.encode()).hexdigest()
'''

# Expected CoT reasoning:
# Step 1: Pattern = MD5 hash for passwords
# Step 2: Exploitability = MEDIUM (rainbow tables)
# Step 3: Impact = MEDIUM (password compromise)
# Step 4: Severity = MEDIUM (not CRITICAL - requires offline attack)
EXPECTED_FINDING_11 = {
    "severity": "MEDIUM",
    "cwe": "CWE-327",
    "reasoning_shown": True,
    "false_positive": False
}

# Test Case 12: Logging with Secrets (True Positive - HIGH, tricky)
LOGGING_SECRET_CODE = '''
import structlog

logger = structlog.get_logger()

def authenticate(username: str, password: str) -> bool:
    # VULNERABILITY: Logging sensitive data
    logger.info("auth_attempt", username=username, password=password)
    return check_credentials(username, password)
'''

# This is tricky - CoT should help classify as HIGH not CRITICAL
# Step 1: Pattern = logging sensitive data
# Step 2: Exploitability = MEDIUM (requires log access)
# Step 3: Impact = HIGH (password exposure)
# Step 4: Severity = HIGH (not CRITICAL - requires log access)
EXPECTED_FINDING_12 = {
    "severity": "HIGH",
    "cwe": "CWE-532",
    "reasoning_shown": True,
    "false_positive": False
}

# Test Case 13: False Positive Risk - UUID in variable name
UUID_VARIABLE_CODE = '''
import uuid

def generate_api_key() -> str:
    # NOT A VULNERABILITY: Generated UUID, not hardcoded secret
    api_key_uuid = uuid.uuid4()
    return f"key_{api_key_uuid}"
'''

# Without CoT, agent might flag "api_key" keyword
# With CoT:
# Step 1: Pattern = "api_key" in variable name
# Step 2: Actual value = uuid.uuid4() (generated, not hardcoded)
# Step 3: No vulnerability
EXPECTED_FINDING_13 = {
    "severity": None,
    "false_positive": False  # CoT should prevent false positive
}

# Test Suite Summary
TEST_CASES = [
    ("SQL Injection", SQL_INJECTION_CODE, EXPECTED_FINDING_1),
    ("Safe SQL", SAFE_SQL_CODE, EXPECTED_FINDING_2),
    ("Hardcoded Secret", HARDCODED_SECRET_CODE, EXPECTED_FINDING_3),
    ("Safe Secret", SAFE_SECRET_CODE, EXPECTED_FINDING_4),
    ("Command Injection", COMMAND_INJECTION_CODE, EXPECTED_FINDING_5),
    ("Safe Subprocess", SAFE_SUBPROCESS_CODE, EXPECTED_FINDING_6),
    ("Pickle Vuln", PICKLE_VULN_CODE, EXPECTED_FINDING_7),
    ("Safe Deserialize", SAFE_DESERIALIZE_CODE, EXPECTED_FINDING_8),
    ("Path Traversal", PATH_TRAVERSAL_CODE, EXPECTED_FINDING_9),
    ("Safe Path", SAFE_PATH_CODE, EXPECTED_FINDING_10),
    ("Weak Hash", WEAK_HASH_CODE, EXPECTED_FINDING_11),
    ("Logging Secret", LOGGING_SECRET_CODE, EXPECTED_FINDING_12),
    ("UUID Variable", UUID_VARIABLE_CODE, EXPECTED_FINDING_13),
]

# Expected outcomes:
# - 8 vulnerabilities (TC1, TC3, TC5, TC7, TC9, TC11, TC12, TC13 if false positive)
# - 5 safe code samples (TC2, TC4, TC6, TC8, TC10, TC13 if correct)
# - CoT should improve precision on edge cases (TC11, TC12, TC13)
