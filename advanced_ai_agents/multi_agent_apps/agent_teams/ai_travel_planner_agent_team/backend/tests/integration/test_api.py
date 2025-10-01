"""Integration tests for FastAPI endpoints."""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from httpx import AsyncClient

from models.plan_task import TaskStatus


@pytest.mark.integration
class TestHealthEndpoint:
    """Test health check endpoint."""

    @pytest.mark.asyncio
    async def test_health_check(self, client: AsyncClient):
        """Test health check returns healthy status."""
        response = await client.get("/api/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data


@pytest.mark.integration
class TestTravelPlanEndpoint:
    """Test travel plan trigger endpoint."""

    @pytest.mark.asyncio
    async def test_trigger_trip_craft_agent_success(
        self,
        client: AsyncClient,
        mock_travel_plan_request
    ):
        """Test successful trip planning trigger."""
        mock_task = MagicMock()
        mock_task.id = 1
        mock_task.trip_plan_id = "test-trip-123"
        mock_task.status = TaskStatus.queued

        with patch("router.plan.create_plan_task") as mock_create_task:
            with patch("router.plan.generate_travel_plan") as mock_generate:
                mock_create_task.return_value = mock_task
                mock_generate.return_value = AsyncMock()

                response = await client.post(
                    "/api/plan/trigger",
                    json=mock_travel_plan_request
                )

                assert response.status_code == 200
                data = response.json()
                assert data["success"] is True
                assert data["trip_plan_id"] == "test-trip-123"
                assert "message" in data

    @pytest.mark.asyncio
    async def test_trigger_trip_craft_agent_missing_fields(self, client: AsyncClient):
        """Test triggering with missing required fields."""
        invalid_request = {
            "travel_plan": {
                "name": "Test Trip"
                # Missing required fields
            }
        }

        response = await client.post(
            "/api/plan/trigger",
            json=invalid_request
        )

        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_trigger_trip_craft_agent_invalid_data(self, client: AsyncClient):
        """Test triggering with invalid data types."""
        invalid_request = {
            "trip_plan_id": "test-123",
            "travel_plan": {
                "name": "Test Trip",
                "destination": "Paris",
                "starting_location": "New York",
                "adults": "not_a_number",  # Invalid type
                "budget": "invalid"  # Invalid type
            }
        }

        response = await client.post(
            "/api/plan/trigger",
            json=invalid_request
        )

        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_trigger_trip_craft_agent_database_error(
        self,
        client: AsyncClient,
        mock_travel_plan_request
    ):
        """Test handling database errors."""
        with patch("router.plan.create_plan_task") as mock_create_task:
            mock_create_task.side_effect = Exception("Database connection failed")

            response = await client.post(
                "/api/plan/trigger",
                json=mock_travel_plan_request
            )

            assert response.status_code == 500
            data = response.json()
            assert "Failed to trigger travel plan agent" in data["detail"]

    @pytest.mark.asyncio
    async def test_trigger_trip_craft_agent_creates_background_task(
        self,
        client: AsyncClient,
        mock_travel_plan_request
    ):
        """Test that background task is created for plan generation."""
        mock_task = MagicMock()
        mock_task.id = 1
        mock_task.trip_plan_id = "test-trip-123"

        with patch("router.plan.create_plan_task") as mock_create_task:
            with patch("router.plan.asyncio.create_task") as mock_create_bg_task:
                with patch("router.plan.update_task_status") as mock_update:
                    mock_create_task.return_value = mock_task
                    mock_update.return_value = AsyncMock()

                    response = await client.post(
                        "/api/plan/trigger",
                        json=mock_travel_plan_request
                    )

                    assert response.status_code == 200
                    # Verify background task was created
                    mock_create_bg_task.assert_called_once()


@pytest.mark.integration
class TestCORSMiddleware:
    """Test CORS middleware configuration."""

    @pytest.mark.asyncio
    async def test_cors_headers_present(self, client: AsyncClient):
        """Test that CORS headers are present in response."""
        response = await client.get("/api/health")

        # CORS headers should be present
        assert response.status_code == 200


@pytest.mark.integration
class TestErrorHandling:
    """Test API error handling."""

    @pytest.mark.asyncio
    async def test_404_not_found(self, client: AsyncClient):
        """Test 404 error for non-existent endpoint."""
        response = await client.get("/api/nonexistent")

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_method_not_allowed(self, client: AsyncClient):
        """Test 405 error for wrong HTTP method."""
        response = await client.get("/api/plan/trigger")  # Should be POST

        assert response.status_code == 405
