"""Tests for structured logging functionality."""

import logging
import json
from unittest.mock import patch, MagicMock
from app.logging_config import setup_logging, StructuredLogger


class TestStructuredLogging:
    """Test cases for structured logging configuration."""

    def test_setup_logging_configures_root_logger(self):
        """Test that setup_logging properly configures the root logger."""
        with patch("logging.basicConfig") as mock_basic_config:
            setup_logging("DEBUG")

            mock_basic_config.assert_called_once()
            call_args = mock_basic_config.call_args[1]
            assert call_args["level"] == logging.DEBUG
            assert "format" in call_args

    def test_structured_logger_creates_json_format(self):
        """Test that StructuredLogger creates properly formatted JSON logs."""
        structured_logger = StructuredLogger("test_service")

        with patch("logging.Logger.info") as mock_info:
            structured_logger.info(
                "Test message", extra={"user_id": "123", "action": "test"}
            )

            # Get the log message that was passed to the logger
            call_args = mock_info.call_args[0]
            log_data = json.loads(call_args[0])

            assert log_data["message"] == "Test message"
            assert log_data["service"] == "test_service"
            assert log_data["user_id"] == "123"
            assert log_data["action"] == "test"
            assert "timestamp" in log_data

    def test_correlation_id_filter_adds_correlation_id(self):
        """Test that correlation ID filter adds correlation ID to log records."""
        from app.logging_config import CorrelationIdFilter

        filter_obj = CorrelationIdFilter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="test message",
            args=(),
            exc_info=None,
        )

        # Test with correlation ID set
        correlation_id = "test-correlation-id-123"
        with patch(
            "app.logging_config.correlation_id_var",
            MagicMock(get=MagicMock(return_value=correlation_id)),
        ):
            result = filter_obj.filter(record)
            assert result is True
            assert hasattr(record, "correlation_id")
            assert record.correlation_id == correlation_id

    def test_structured_logger_error_logging(self):
        """Test that structured logger properly formats error logs."""
        structured_logger = StructuredLogger("test_service")

        with patch("logging.Logger.error") as mock_error:
            try:
                raise ValueError("Test error")
            except ValueError:
                structured_logger.error(
                    "Error occurred", exc_info=True, extra={"operation": "test_op"}
                )

                call_args = mock_error.call_args[0]
                log_data = json.loads(call_args[0])

                assert log_data["message"] == "Error occurred"
                assert log_data["operation"] == "test_op"
                assert "exception" in log_data

    async def test_correlation_id_middleware_generates_new_id(self):
        """Test that correlation ID middleware generates new correlation ID when not present."""
        from app.logging_config import CorrelationIdMiddleware

        # Mock FastAPI Request and Response
        request = MagicMock()
        request.headers = {}

        response = MagicMock()
        response.headers = {}

        async def mock_call_next(req):
            return response

        middleware = CorrelationIdMiddleware()

        # Test middleware generates a new correlation ID
        test_uuid = "test-correlation-id-123"
        with patch("uuid.uuid4", return_value=MagicMock(hex=test_uuid)):
            with patch("app.logging_config.correlation_id_var") as mock_var:
                mock_var.set = MagicMock()
                result = await middleware.dispatch(request, mock_call_next)

                # Check that correlation ID was set in context and then cleared
                assert mock_var.set.call_count == 2
                mock_var.set.assert_any_call(test_uuid)
                mock_var.set.assert_any_call(None)

                # Check that response was returned
                assert result == response

                # Check that correlation ID was added to response headers
                assert response.headers["X-Correlation-ID"] == test_uuid

    async def test_correlation_id_middleware_uses_existing_header(self):
        """Test that middleware uses existing X-Correlation-ID header if present."""
        from app.logging_config import CorrelationIdMiddleware

        # Mock FastAPI Request with existing correlation ID
        existing_id = "existing-correlation-id-456"
        request = MagicMock()
        request.headers = {"X-Correlation-ID": existing_id}

        response = MagicMock()
        response.headers = {}

        async def mock_call_next(req):
            return response

        middleware = CorrelationIdMiddleware()

        # Test middleware uses existing correlation ID
        with patch("app.logging_config.correlation_id_var") as mock_var:
            mock_var.set = MagicMock()
            result = await middleware.dispatch(request, mock_call_next)

            # Check that existing correlation ID was used
            assert mock_var.set.call_count == 2
            mock_var.set.assert_any_call(existing_id)
            mock_var.set.assert_any_call(None)

            # Check that response was returned
            assert result == response

            # Check that correlation ID was added to response headers
            assert response.headers["X-Correlation-ID"] == existing_id

    def test_structured_logger_includes_correlation_id(self):
        """Test that structured logger includes correlation ID when available."""
        structured_logger = StructuredLogger("test_service")
        correlation_id = "test-correlation-id-123"

        with patch(
            "app.logging_config.correlation_id_var",
            MagicMock(get=MagicMock(return_value=correlation_id)),
        ):
            with patch("logging.Logger.info") as mock_info:
                structured_logger.info("Test message")

                call_args = mock_info.call_args[0]
                log_data = json.loads(call_args[0])

                assert log_data["correlation_id"] == correlation_id
