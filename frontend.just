set working-directory := 'frontend'

lint *FILES="":
    npm run lint{{ if FILES != "" { " -- " + replace_regex(FILES, "frontend/", "") } else { "" } }}

test:
    npm run test:run \-- \--reporter=verbose \--passWithNoTests

type-check:
    npm run type-check
