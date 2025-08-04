# Correlation ID Middleware Documentation

## Overview

The Correlation ID Middleware generates unique identifiers for each HTTP request, enabling request tracing across distributed systems and improving debugging capabilities. This middleware is integrated into the FastAPI application and works seamlessly with the structured logging system.

## Features

- **Automatic ID Generation**: Creates unique correlation IDs for requests without existing IDs
- **ID Preservation**: Preserves existing correlation IDs from incoming request headers
- **Context Propagation**: Sets correlation IDs in context variables for use throughout the request lifecycle
- **Response Headers**: Adds correlation IDs to response headers for client-side tracking
- **Logging Integration**: Automatically includes correlation IDs in all log messages during request processing

## Implementation Details

### Middleware Class

Located in `backend/app/logging_config.py`:

```python
class CorrelationIdMiddleware:
    """Middleware to generate correlation IDs for requests."""

    async def dispatch(self, request: Any, call_next: Any) -> Any:
        """Generate and set correlation IDs for requests."""
        import uuid

        # Generate a new correlation ID if not present in headers
        correlation_id = request.headers.get("X-Correlation-ID")
        if not correlation_id:
            correlation_id = uuid.uuid4().hex

        # Set the correlation ID in the context variable
        correlation_id_var.set(correlation_id)

        try:
            # Process the request
            response = await call_next(request)

            # Add correlation ID to response headers
            response.headers["X-Correlation-ID"] = correlation_id

            return response
        finally:
            # Clear the context variable after the request
            correlation_id_var.set(None)
```

### Integration with FastAPI

The middleware is registered in `backend/app/main.py`:

```python
from starlette.middleware.base import BaseHTTPMiddleware
from .logging_config import CorrelationIdMiddleware

# Add correlation ID middleware
app.add_middleware(BaseHTTPMiddleware, dispatch=CorrelationIdMiddleware(app).dispatch)
```

### Context Variable

The correlation ID is stored in a context variable for thread-safe access:

```python
from contextvars import ContextVar

correlation_id_var: ContextVar[Optional[str]] = ContextVar(
    "correlation_id", default=None
)
```

## Usage

### Client-Side Usage

Clients can:
1. **Provide their own correlation ID**: Include `X-Correlation-ID` header in requests
2. **Receive generated IDs**: Check the `X-Correlation-ID` response header

Example with curl:
```bash
# With custom correlation ID
curl -H "X-Correlation-ID: my-custom-id-123" http://localhost:8000/occupation_ids

# Without correlation ID (one will be generated)
curl -v http://localhost:8000/occupation_ids
```

### Server-Side Usage

The correlation ID is automatically available in:
- **Log messages**: Via the `CorrelationIdFilter`
- **Application code**: Via `correlation_id_var.get()`
- **Structured logs**: The `StructuredLogger` class automatically includes correlation IDs in all JSON log messages

Example with StructuredLogger:
```python
from app.logging_config import StructuredLogger

logger = StructuredLogger("my_service")
logger.info("Processing request")  # Will include correlation_id in JSON output
```

Example in application code:
```python
from app.logging_config import correlation_id_var

def some_function():
    correlation_id = correlation_id_var.get()
    if correlation_id:
        # Use correlation ID for tracking
        logger.info(f"Processing request {correlation_id}")
```

## Testing

The middleware includes comprehensive tests:

### Unit Tests
Located in `backend/tests/unit/test_logging.py`:
- `test_correlation_id_middleware_generates_new_id`: Verifies ID generation
- `test_correlation_id_middleware_uses_existing_header`: Verifies ID preservation

### Integration Tests
Located in `backend/tests/integration/test_api_integration.py`:
- `test_correlation_id_generated_for_request`: Verifies end-to-end ID generation
- `test_correlation_id_preserved_from_request_header`: Verifies ID preservation in full request cycle

## Benefits

1. **Request Tracing**: Track requests across multiple services and components
2. **Debugging**: Easily correlate logs for a specific request
3. **Performance Monitoring**: Measure request processing time across services
4. **Error Investigation**: Group all logs related to a failed request
5. **Audit Trail**: Maintain complete request history for compliance

## Best Practices

1. **Log Correlation IDs**: Include correlation IDs in all log messages
2. **Propagate to External Services**: Pass correlation IDs to downstream services
3. **Store in Error Reports**: Include correlation IDs in error tracking systems
4. **Monitor Unique IDs**: Ensure correlation IDs remain unique across requests
5. **Use in Distributed Tracing**: Integrate with tools like Jaeger or Zipkin

## Troubleshooting

### Missing Correlation IDs in Logs
- Ensure `CorrelationIdFilter` is added to loggers
- Verify middleware is registered before request processing

### Correlation IDs Not in Response Headers
- Check middleware registration order in FastAPI
- Ensure response object supports header modification

### Context Variable Issues
- Verify async context propagation in async handlers
- Check for context clearing in error scenarios

## Future Enhancements

1. **Distributed Tracing Integration**: Connect with OpenTelemetry or similar
2. **ID Format Configuration**: Support different ID formats (UUID, custom)
3. **Header Name Configuration**: Allow customizable header names
4. **Metrics Collection**: Track correlation ID usage statistics
5. **Log Aggregation**: Integration with centralized logging systems
