"""Unit tests for Pydantic models."""
import pytest
from pydantic import ValidationError
from models.travel_plan import (
    TravelDates,
    TravelPlanRequest,
    TravelPlanAgentRequest,
    TravelPlanResponse,
    DayByDayPlan,
    Attraction,
    FlightResult,
    RestaurantResult,
    TravelPlanTeamResponse,
)
from models.plan_task import TaskStatus


@pytest.mark.unit
class TestTravelDates:
    """Test TravelDates model."""

    def test_travel_dates_creation(self):
        """Test creating TravelDates with valid data."""
        dates = TravelDates(start="2025-06-01", end="2025-06-10")
        assert dates.start == "2025-06-01"
        assert dates.end == "2025-06-10"

    def test_travel_dates_defaults(self):
        """Test TravelDates with default values."""
        dates = TravelDates()
        assert dates.start == ""
        assert dates.end == ""


@pytest.mark.unit
class TestTravelPlanRequest:
    """Test TravelPlanRequest model."""

    def test_travel_plan_request_creation(self):
        """Test creating TravelPlanRequest with valid data."""
        plan = TravelPlanRequest(
            name="Paris Trip",
            destination="Paris, France",
            starting_location="New York, USA",
            travel_dates=TravelDates(start="2025-06-01", end="2025-06-10"),
            duration=9,
            adults=2,
            budget=5000,
            budget_currency="USD",
        )
        assert plan.name == "Paris Trip"
        assert plan.destination == "Paris, France"
        assert plan.adults == 2
        assert plan.budget == 5000

    def test_travel_plan_request_defaults(self):
        """Test TravelPlanRequest with default values."""
        plan = TravelPlanRequest()
        assert plan.name == ""
        assert plan.adults == 1
        assert plan.children == 0
        assert plan.budget == 75000
        assert plan.budget_currency == "INR"
        assert plan.vibes == []
        assert plan.pace == [3]


@pytest.mark.unit
class TestTravelPlanAgentRequest:
    """Test TravelPlanAgentRequest model."""

    def test_agent_request_creation(self):
        """Test creating TravelPlanAgentRequest."""
        travel_plan = TravelPlanRequest(name="Test Trip", destination="Paris")
        agent_request = TravelPlanAgentRequest(
            trip_plan_id="test-123",
            travel_plan=travel_plan
        )
        assert agent_request.trip_plan_id == "test-123"
        assert agent_request.travel_plan.name == "Test Trip"

    def test_agent_request_missing_fields(self):
        """Test TravelPlanAgentRequest with missing required fields."""
        with pytest.raises(ValidationError):
            TravelPlanAgentRequest(travel_plan=TravelPlanRequest())


@pytest.mark.unit
class TestTravelPlanResponse:
    """Test TravelPlanResponse model."""

    def test_response_creation(self):
        """Test creating TravelPlanResponse."""
        response = TravelPlanResponse(
            success=True,
            message="Success",
            trip_plan_id="test-123"
        )
        assert response.success is True
        assert response.message == "Success"
        assert response.trip_plan_id == "test-123"


@pytest.mark.unit
class TestDayByDayPlan:
    """Test DayByDayPlan model."""

    def test_day_plan_creation(self):
        """Test creating DayByDayPlan."""
        plan = DayByDayPlan(
            day=1,
            date="2025-06-01",
            morning="Visit Eiffel Tower",
            afternoon="Louvre Museum",
            evening="Seine River Cruise",
            notes="Book tickets in advance"
        )
        assert plan.day == 1
        assert plan.morning == "Visit Eiffel Tower"
        assert plan.notes == "Book tickets in advance"

    def test_day_plan_defaults(self):
        """Test DayByDayPlan with defaults."""
        plan = DayByDayPlan()
        assert plan.day == 0
        assert plan.date == ""
        assert plan.morning == ""


@pytest.mark.unit
class TestAttraction:
    """Test Attraction model."""

    def test_attraction_creation(self):
        """Test creating Attraction."""
        attraction = Attraction(
            name="Eiffel Tower",
            description="Iconic iron lattice tower"
        )
        assert attraction.name == "Eiffel Tower"
        assert "iron lattice" in attraction.description


@pytest.mark.unit
class TestFlightResult:
    """Test FlightResult model."""

    def test_flight_creation(self):
        """Test creating FlightResult."""
        flight = FlightResult(
            duration="8h 30m",
            price="$650",
            departure_time="10:00 AM",
            arrival_time="11:30 PM",
            airline="Air France",
            flight_number="AF123",
            url="https://example.com",
            stops=0
        )
        assert flight.airline == "Air France"
        assert flight.stops == 0
        assert flight.price == "$650"


@pytest.mark.unit
class TestRestaurantResult:
    """Test RestaurantResult model."""

    def test_restaurant_creation(self):
        """Test creating RestaurantResult."""
        restaurant = RestaurantResult(
            name="Le Jules Verne",
            description="Fine dining at Eiffel Tower",
            location="Eiffel Tower, 2nd floor",
            url="https://example.com"
        )
        assert restaurant.name == "Le Jules Verne"
        assert "Eiffel Tower" in restaurant.location


@pytest.mark.unit
class TestTravelPlanTeamResponse:
    """Test TravelPlanTeamResponse model."""

    def test_team_response_creation(self):
        """Test creating TravelPlanTeamResponse."""
        response = TravelPlanTeamResponse(
            day_by_day_plan=[
                DayByDayPlan(day=1, date="2025-06-01", morning="Activity")
            ],
            hotels=[],
            attractions=[Attraction(name="Louvre", description="Museum")],
            flights=[],
            restaurants=[],
            budget_insights=["Stay within budget"],
            tips=["Book early"]
        )
        assert len(response.day_by_day_plan) == 1
        assert len(response.attractions) == 1
        assert response.tips[0] == "Book early"


@pytest.mark.unit
class TestTaskStatus:
    """Test TaskStatus enum."""

    def test_task_status_values(self):
        """Test TaskStatus enum values."""
        assert TaskStatus.queued.value == "queued"
        assert TaskStatus.in_progress.value == "in_progress"
        assert TaskStatus.success.value == "success"
        assert TaskStatus.error.value == "error"

    def test_task_status_case_insensitive(self):
        """Test TaskStatus case-insensitive lookup."""
        assert TaskStatus._missing_("QUEUED") == TaskStatus.queued
        assert TaskStatus._missing_("In_Progress") == TaskStatus.in_progress
        assert TaskStatus._missing_("SUCCESS") == TaskStatus.success
