set working-directory := 'backend'

test:
    pytest

unit-test:
    pytest tests/unit/ -x --tb=short -q

lint *FILES="":
    ruff check {{ if FILES == "" { "." } else { replace_regex(FILES, "^backend/", "") } }} --fix

format *FILES="":
    ruff format {{ if FILES == "" { "." } else { replace_regex(FILES, "^backend/", "") } }}

type-check *FILES="":
    mypy {{ if FILES == "" { "." } else { replace_regex(FILES, "^backend/", "") } }}
