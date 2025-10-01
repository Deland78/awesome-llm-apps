import pytest
import asyncio
from typing import AsyncGenerator
from httpx import AsyncClient, ASGITransport
from unittest.mock import AsyncMock, MagicMock, patch
import sys
import os

# Add parent directory to path to import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Mock environment variables before importing app
os.environ.setdefault('EXA_API_KEY', 'test_key')
os.environ.setdefault('GOOGLE_API_KEY', 'test_key')
os.environ.setdefault('FIRECRAWL_API_KEY', 'test_key')
os.environ.setdefault('DATABASE_URL', 'postgresql://test:test@localhost:5432/test')

from api.app import app


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    """Create an async HTTP client for testing FastAPI endpoints."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        yield ac


@pytest.fixture
def mock_db_pool():
    """Mock database connection pool."""
    pool = AsyncMock()
    pool.acquire = AsyncMock()
    pool.release = AsyncMock()
    return pool


@pytest.fixture
def mock_travel_plan_request():
    """Mock travel plan request data."""
    return {
        "trip_plan_id": "test-trip-123",
        "travel_plan": {
            "name": "Paris Adventure",
            "destination": "Paris, France",
            "starting_location": "New York, USA",
            "travel_dates": {
                "start": "2025-06-01",
                "end": "2025-06-10"
            },
            "date_input_type": "picker",
            "duration": 9,
            "traveling_with": "partner",
            "adults": 2,
            "children": 0,
            "age_groups": [],
            "budget": 5000,
            "budget_currency": "USD",
            "travel_style": "luxury",
            "budget_flexible": True,
            "vibes": ["romantic", "cultural"],
            "priorities": ["attractions", "food"],
            "interests": "art museums, fine dining",
            "rooms": 1,
            "pace": [3],
            "been_there_before": "no",
            "loved_places": "",
            "additional_info": "Looking for authentic experiences"
        }
    }


@pytest.fixture
def mock_travel_plan_model():
    """Mock TravelPlan model instance."""
    from models.travel_plan import TravelPlan

    return TravelPlan(
        name="Paris Adventure",
        destination="Paris, France",
        starting_location="New York, USA",
        travel_dates={"start": "2025-06-01", "end": "2025-06-10"},
        date_input_type="picker",
        duration=9,
        traveling_with="partner",
        adults=2,
        children=0,
        age_groups=[],
        budget=5000,
        budget_currency="USD",
        travel_style="luxury",
        budget_flexible=True,
        vibes=["romantic", "cultural"],
        priorities=["attractions", "food"],
        interests="art museums, fine dining",
        rooms=1,
        pace=[3],
        been_there_before="no",
        loved_places="",
        additional_info="Looking for authentic experiences"
    )


@pytest.fixture
def mock_plan_task():
    """Mock PlanTask instance."""
    return MagicMock(
        id="task-123",
        trip_plan_id="test-trip-123",
        task_type="travel_plan_generation",
        status="pending"
    )
