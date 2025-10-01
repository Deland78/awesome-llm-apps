"""Unit tests for repository functions."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timezone

from models.plan_task import PlanTask, TaskStatus
from repository.plan_task_repository import (
    create_plan_task,
    update_task_status,
    get_task_by_id,
    get_tasks_by_trip_plan,
    get_tasks_by_status,
)


@pytest.mark.unit
class TestPlanTaskRepository:
    """Test plan task repository functions."""

    @pytest.mark.asyncio
    async def test_create_plan_task(self):
        """Test creating a plan task."""
        mock_session = AsyncMock()
        mock_task = PlanTask(
            id=1,
            trip_plan_id="test-123",
            task_type="travel_plan_generation",
            status=TaskStatus.queued,
            input_data={"test": "data"},
        )

        mock_session.add = MagicMock()
        mock_session.commit = AsyncMock()
        mock_session.refresh = AsyncMock()

        with patch("repository.plan_task_repository.get_db_session") as mock_get_session:
            mock_get_session.return_value.__aenter__.return_value = mock_session

            # Mock the task creation
            with patch.object(PlanTask, "__init__", return_value=None):
                task = await create_plan_task(
                    trip_plan_id="test-123",
                    task_type="travel_plan_generation",
                    input_data={"test": "data"}
                )

            mock_session.add.assert_called_once()
            mock_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_task_status_success(self):
        """Test updating task status to success."""
        mock_session = AsyncMock()
        mock_task = MagicMock(spec=PlanTask)
        mock_task.id = 1
        mock_task.status = TaskStatus.queued

        mock_result = MagicMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=mock_task)
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_session.commit = AsyncMock()
        mock_session.refresh = AsyncMock()

        with patch("repository.plan_task_repository.get_db_session") as mock_get_session:
            mock_get_session.return_value.__aenter__.return_value = mock_session

            task = await update_task_status(
                task_id=1,
                status=TaskStatus.success,
                output_data={"result": "success"}
            )

            assert mock_task.status == TaskStatus.success
            assert mock_task.output_data == {"result": "success"}
            mock_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_task_status_error(self):
        """Test updating task status to error."""
        mock_session = AsyncMock()
        mock_task = MagicMock(spec=PlanTask)
        mock_task.id = 1
        mock_task.status = TaskStatus.in_progress

        mock_result = MagicMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=mock_task)
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_session.commit = AsyncMock()
        mock_session.refresh = AsyncMock()

        with patch("repository.plan_task_repository.get_db_session") as mock_get_session:
            mock_get_session.return_value.__aenter__.return_value = mock_session

            task = await update_task_status(
                task_id=1,
                status=TaskStatus.error,
                error_message="Test error"
            )

            assert mock_task.status == TaskStatus.error
            assert mock_task.error_message == "Test error"

    @pytest.mark.asyncio
    async def test_update_task_status_not_found(self):
        """Test updating task status when task doesn't exist."""
        mock_session = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=None)
        mock_session.execute = AsyncMock(return_value=mock_result)

        with patch("repository.plan_task_repository.get_db_session") as mock_get_session:
            mock_get_session.return_value.__aenter__.return_value = mock_session

            task = await update_task_status(
                task_id=999,
                status=TaskStatus.success
            )

            assert task is None

    @pytest.mark.asyncio
    async def test_get_task_by_id(self):
        """Test getting task by ID."""
        mock_session = AsyncMock()
        mock_task = MagicMock(spec=PlanTask)
        mock_task.id = 1

        mock_result = MagicMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=mock_task)
        mock_session.execute = AsyncMock(return_value=mock_result)

        with patch("repository.plan_task_repository.get_db_session") as mock_get_session:
            mock_get_session.return_value.__aenter__.return_value = mock_session

            task = await get_task_by_id(1)

            assert task == mock_task
            assert task.id == 1

    @pytest.mark.asyncio
    async def test_get_tasks_by_trip_plan(self):
        """Test getting all tasks for a trip plan."""
        mock_session = AsyncMock()
        mock_tasks = [
            MagicMock(spec=PlanTask, trip_plan_id="test-123"),
            MagicMock(spec=PlanTask, trip_plan_id="test-123"),
        ]

        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.all = MagicMock(return_value=mock_tasks)
        mock_result.scalars = MagicMock(return_value=mock_scalars)
        mock_session.execute = AsyncMock(return_value=mock_result)

        with patch("repository.plan_task_repository.get_db_session") as mock_get_session:
            mock_get_session.return_value.__aenter__.return_value = mock_session

            tasks = await get_tasks_by_trip_plan("test-123")

            assert len(tasks) == 2
            assert all(t.trip_plan_id == "test-123" for t in tasks)

    @pytest.mark.asyncio
    async def test_get_tasks_by_status(self):
        """Test getting tasks by status."""
        mock_session = AsyncMock()
        mock_tasks = [
            MagicMock(spec=PlanTask, status=TaskStatus.queued),
            MagicMock(spec=PlanTask, status=TaskStatus.queued),
        ]

        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.all = MagicMock(return_value=mock_tasks)
        mock_result.scalars = MagicMock(return_value=mock_scalars)
        mock_session.execute = AsyncMock(return_value=mock_result)

        with patch("repository.plan_task_repository.get_db_session") as mock_get_session:
            mock_get_session.return_value.__aenter__.return_value = mock_session

            tasks = await get_tasks_by_status(TaskStatus.queued)

            assert len(tasks) == 2
            assert all(t.status == TaskStatus.queued for t in tasks)

    @pytest.mark.asyncio
    async def test_get_tasks_by_status_empty(self):
        """Test getting tasks by status when none exist."""
        mock_session = AsyncMock()
        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.all = MagicMock(return_value=[])
        mock_result.scalars = MagicMock(return_value=mock_scalars)
        mock_session.execute = AsyncMock(return_value=mock_result)

        with patch("repository.plan_task_repository.get_db_session") as mock_get_session:
            mock_get_session.return_value.__aenter__.return_value = mock_session

            tasks = await get_tasks_by_status(TaskStatus.success)

            assert len(tasks) == 0
