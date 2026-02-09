"""
Test cases for hallucination-detector with Chain-of-Thought reasoning.

Purpose: Measure accuracy improvement from CoT prompting.
Expected: +15-25% precision on hallucination classification (fewer false positives on edge cases).
"""

# Test Case 1: Pydantic v1 syntax in v2 codebase (True Positive - DEPRECATED_API)
PYDANTIC_V1_CODE = '''
from pydantic import BaseModel, validator

class User(BaseModel):
    email: str
    age: int

    @validator('email')
    def validate_email(cls, v):
        if '@' not in v:
            raise ValueError('Invalid email')
        return v
'''

# Expected CoT reasoning:
# Step 1: Extract pattern = @validator decorator
# Step 2: Query Context7 = "pydantic field validator v2"
# Step 3: Compare = @validator (v1) vs @field_validator (v2)
# Step 4: Classify = DEPRECATED_API
# Step 5: Verify fix = @field_validator('email', mode='after')
# Step 6: Confidence = HIGH (99%) - direct match
EXPECTED_FINDING_1 = {
    "hallucination_type": "DEPRECATED_API",
    "library": "pydantic",
    "confidence": "HIGH",
    "reasoning_shown": True,
    "false_positive": False
}

# Test Case 2: Pydantic v2 correct syntax (True Negative)
PYDANTIC_V2_CODE = '''
from pydantic import BaseModel, field_validator

class User(BaseModel):
    email: str
    age: int

    @field_validator('email', mode='after')
    def validate_email(cls, v):
        if '@' not in v:
            raise ValueError('Invalid email')
        return v
'''

EXPECTED_FINDING_2 = {
    "hallucination_type": None,
    "confidence": "HIGH",
    "false_positive": False
}

# Test Case 3: Anthropic deprecated parameter (True Positive - INVALID_PARAMETER)
ANTHROPIC_OLD_CODE = '''
from anthropic import Anthropic

client = Anthropic(api_key="sk-xxx")
response = client.messages.create(
    model="claude-3-opus-20240229",
    max_tokens_to_sample=1024,  # DEPRECATED parameter
    messages=[{"role": "user", "content": "Hello"}]
)
'''

# Expected CoT reasoning:
# Step 1: Extract pattern = max_tokens_to_sample parameter
# Step 2: Query Context7 = "Anthropic messages.create parameters"
# Step 3: Compare = max_tokens_to_sample (old) vs max_tokens (new)
# Step 4: Classify = INVALID_PARAMETER (deprecated)
# Step 5: Verify fix = max_tokens=1024
# Step 6: Confidence = HIGH (99%)
EXPECTED_FINDING_3 = {
    "hallucination_type": "INVALID_PARAMETER",
    "library": "anthropic",
    "confidence": "HIGH",
    "reasoning_shown": True,
    "false_positive": False
}

# Test Case 4: Anthropic correct parameter (True Negative)
ANTHROPIC_NEW_CODE = '''
from anthropic import Anthropic

client = Anthropic(api_key="sk-xxx")
response = client.messages.create(
    model="claude-3-opus-20240229",
    max_tokens=1024,  # Correct parameter
    messages=[{"role": "user", "content": "Hello"}]
)
'''

EXPECTED_FINDING_4 = {
    "hallucination_type": None,
    "confidence": "HIGH",
    "false_positive": False
}

# Test Case 5: httpx invalid timeout type (True Positive - INVALID_PARAMETER)
HTTPX_WRONG_TIMEOUT_CODE = '''
import httpx

async def fetch_data():
    async with httpx.AsyncClient(timeout=30) as client:  # Wrong: should be Timeout object
        response = await client.get("https://api.example.com")
        return response.json()
'''

# Expected CoT reasoning:
# Step 1: Extract pattern = timeout=30 (int)
# Step 2: Query Context7 = "httpx AsyncClient timeout configuration"
# Step 3: Compare = timeout=30 vs timeout=httpx.Timeout(30.0)
# Step 4: Classify = INVALID_PARAMETER (wrong type)
# Step 5: Verify fix = httpx.Timeout(30.0)
# Step 6: Confidence = HIGH (99%)
EXPECTED_FINDING_5 = {
    "hallucination_type": "INVALID_PARAMETER",
    "library": "httpx",
    "confidence": "HIGH",
    "reasoning_shown": True,
    "false_positive": False
}

# Test Case 6: httpx correct timeout (True Negative)
HTTPX_CORRECT_TIMEOUT_CODE = '''
import httpx

async def fetch_data():
    async with httpx.AsyncClient(timeout=httpx.Timeout(30.0)) as client:
        response = await client.get("https://api.example.com")
        return response.json()
'''

EXPECTED_FINDING_6 = {
    "hallucination_type": None,
    "confidence": "HIGH",
    "false_positive": False
}

# Test Case 7: LangGraph invented method (True Positive - INVENTED_METHOD)
LANGGRAPH_INVENTED_CODE = '''
from langgraph.graph import StateGraph

class PipelineState(TypedDict):
    messages: list[str]

# HALLUCINATION: StateGraph.create() doesn't exist
graph = StateGraph.create(state_schema=PipelineState)
'''

# Expected CoT reasoning:
# Step 1: Extract pattern = StateGraph.create()
# Step 2: Query Context7 = "LangGraph StateGraph initialization"
# Step 3: Compare = .create() vs direct initialization
# Step 4: Classify = INVENTED_METHOD
# Step 5: Verify fix = StateGraph(PipelineState)
# Step 6: Confidence = HIGH (99%)
EXPECTED_FINDING_7 = {
    "hallucination_type": "INVENTED_METHOD",
    "library": "langgraph",
    "confidence": "HIGH",
    "reasoning_shown": True,
    "false_positive": False
}

# Test Case 8: LangGraph correct initialization (True Negative)
LANGGRAPH_CORRECT_CODE = '''
from langgraph.graph import StateGraph

class PipelineState(TypedDict):
    messages: list[str]

# Correct initialization
graph = StateGraph(PipelineState)
'''

EXPECTED_FINDING_8 = {
    "hallucination_type": None,
    "confidence": "HIGH",
    "false_positive": False
}

# Test Case 9: structlog correct usage (True Negative, edge case)
STRUCTLOG_CORRECT_CODE = '''
import structlog

logger = structlog.get_logger()

def process_data(user_id: str):
    logger.info("processing", user_id=user_id)
    # More code...
'''

# This should NOT be flagged as hallucination
# CoT should verify structlog.get_logger() is valid
EXPECTED_FINDING_9 = {
    "hallucination_type": None,
    "confidence": "HIGH",
    "false_positive": False
}

# Test Case 10: typing.List vs list[str] (True Negative, tricky case)
TYPING_MODERN_CODE = '''
from typing import Any

def process_items(items: list[str]) -> dict[str, Any]:
    """Modern type hints (Python 3.10+)."""
    return {item: len(item) for item in items}
'''

# This is CORRECT modern syntax, not a hallucination
# Without CoT, agent might flag as "should use typing.List"
# With CoT:
# Step 1: Extract pattern = list[str]
# Step 2: Query Context7 = "Python type hints modern syntax"
# Step 3: Compare = list[str] is CORRECT for Python 3.10+
# Step 4: No hallucination
# Step 6: Confidence = HIGH (99%)
EXPECTED_FINDING_10 = {
    "hallucination_type": None,
    "confidence": "HIGH",
    "false_positive": False  # CoT prevents false positive
}

# Test Case 11: Pydantic ConfigDict usage (True Negative, recent change)
PYDANTIC_CONFIGDICT_CODE = '''
from pydantic import BaseModel, ConfigDict

class User(BaseModel):
    model_config = ConfigDict(validate_assignment=True, frozen=True)

    email: str
    age: int
'''

# This is CORRECT Pydantic v2 syntax
# CoT should verify ConfigDict is valid
EXPECTED_FINDING_11 = {
    "hallucination_type": None,
    "confidence": "HIGH",
    "false_positive": False
}

# Test Case 12: Mixed valid/invalid (True Positive on one line)
MIXED_CODE = '''
from pydantic import BaseModel, validator, ConfigDict

class User(BaseModel):
    model_config = ConfigDict(validate_assignment=True)  # CORRECT

    email: str

    @validator('email')  # WRONG - should be @field_validator
    def validate_email(cls, v):
        return v
'''

# Expected: Flag only the @validator line, not ConfigDict
EXPECTED_FINDING_12 = {
    "hallucination_type": "DEPRECATED_API",
    "library": "pydantic",
    "line_flagged": "@validator",
    "confidence": "HIGH",
    "reasoning_shown": True,
    "false_positive": False
}

# Test Case 13: Edge case - temperature parameter (boundary value check)
ANTHROPIC_TEMP_CODE = '''
from anthropic import Anthropic

client = Anthropic()
response = client.messages.create(
    model="claude-3-opus-20240229",
    max_tokens=1024,
    temperature=1.5,  # INVALID - max is 1.0
    messages=[{"role": "user", "content": "Hello"}]
)
'''

# Expected CoT reasoning:
# Step 1: Extract pattern = temperature=1.5
# Step 2: Query Context7 = "Anthropic temperature parameter range"
# Step 3: Compare = 1.5 vs valid range [0.0, 1.0]
# Step 4: Classify = INVALID_PARAMETER (out of range)
# Step 5: Verify fix = temperature=1.0 (or lower)
# Step 6: Confidence = HIGH (99%)
EXPECTED_FINDING_13 = {
    "hallucination_type": "INVALID_PARAMETER",
    "library": "anthropic",
    "confidence": "HIGH",
    "reasoning_shown": True,
    "false_positive": False
}

# Test Suite Summary
TEST_CASES = [
    ("Pydantic v1 validator", PYDANTIC_V1_CODE, EXPECTED_FINDING_1),
    ("Pydantic v2 correct", PYDANTIC_V2_CODE, EXPECTED_FINDING_2),
    ("Anthropic old param", ANTHROPIC_OLD_CODE, EXPECTED_FINDING_3),
    ("Anthropic correct", ANTHROPIC_NEW_CODE, EXPECTED_FINDING_4),
    ("httpx wrong timeout", HTTPX_WRONG_TIMEOUT_CODE, EXPECTED_FINDING_5),
    ("httpx correct timeout", HTTPX_CORRECT_TIMEOUT_CODE, EXPECTED_FINDING_6),
    ("LangGraph invented", LANGGRAPH_INVENTED_CODE, EXPECTED_FINDING_7),
    ("LangGraph correct", LANGGRAPH_CORRECT_CODE, EXPECTED_FINDING_8),
    ("structlog correct", STRUCTLOG_CORRECT_CODE, EXPECTED_FINDING_9),
    ("Modern type hints", TYPING_MODERN_CODE, EXPECTED_FINDING_10),
    ("ConfigDict correct", PYDANTIC_CONFIGDICT_CODE, EXPECTED_FINDING_11),
    ("Mixed valid/invalid", MIXED_CODE, EXPECTED_FINDING_12),
    ("Temperature range", ANTHROPIC_TEMP_CODE, EXPECTED_FINDING_13),
]

# Expected outcomes:
# - 6 hallucinations (TC1, TC3, TC5, TC7, TC12, TC13)
# - 7 correct code samples (TC2, TC4, TC6, TC8, TC9, TC10, TC11)
# - CoT should prevent false positives on TC10 (modern syntax)
# - CoT should correctly identify mixed case TC12
