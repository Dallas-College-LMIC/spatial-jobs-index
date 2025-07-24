set working-directory := 'frontend'

lint:
    npm run lint

test:
    npm run test:run -- --reporter=verbose --passWithNoTests

type-check:
    npm run type-check
