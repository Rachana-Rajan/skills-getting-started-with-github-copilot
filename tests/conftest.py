import pytest
from copy import deepcopy
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add src to path so we can import app
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app, activities


@pytest.fixture
def client():
    """Provide a TestClient for the FastAPI app"""
    return TestClient(app)


@pytest.fixture
def sample_activities():
    """Provide a clean copy of activities for each test"""
    return deepcopy(activities)


@pytest.fixture(autouse=True)
def reset_activities(sample_activities):
    """Reset activities dictionary before each test to ensure isolation"""
    # Store original state
    original_state = deepcopy(activities)
    
    # Replace with sample
    activities.clear()
    activities.update(sample_activities)
    
    yield
    
    # Restore after test
    activities.clear()
    activities.update(original_state)
