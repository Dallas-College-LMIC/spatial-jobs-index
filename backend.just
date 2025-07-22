set working-directory := 'backend'

test:
    pytest

unit-test:
    pytest tests/unit/ -x --tb=short -q

lint:
    ruff check . --fix

format:
    ruff format .

typecheck:
    mypy .
