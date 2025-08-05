set working-directory := 'frontend'

lint *FILES="":
    #!/usr/bin/env bash
    if [ -z "{{ FILES }}" ]; then
        npm run lint
    else
        # Remove frontend/ prefix from all files and ensure paths are relative
        files="{{ FILES }}"
        cleaned_files=$(echo "$files" | sed 's|frontend/||g')
        npm run lint -- $cleaned_files
    fi

test:
    npm run test:run \-- \--reporter=verbose \--passWithNoTests

type-check:
    npm run type-check
