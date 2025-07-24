set working-directory := 'backend'

test:
    pytest

unit-test:
    pytest tests/unit/ -x --tb=short -q

lint *FILES:
    ruff check {{if FILES == "" { "." } else { FILES }}} --fix

format *FILES:
    ruff format {{if FILES == "" { "." } else { FILES }}}

type-check *FILES:
    mypy {{if FILES == "" { "." } else { FILES }}}
