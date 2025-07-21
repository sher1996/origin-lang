# E2E Tests

This directory contains end-to-end tests using Playwright for the visual editor.

## Test Files

- `player-highlight.spec.ts` - Tests the player functionality including seeking and block highlighting

## Running Tests

### Local Development
```bash
# Install dependencies
npm install

# Install Playwright browsers
npx playwright install

# Run e2e tests
npm run test:e2e

# Run with UI
npm run test:e2e:ui

# Run in headed mode (shows browser)
npm run test:e2e:headed
```

### CI/CD
The e2e tests are automatically run in the CI pipeline on:
- Push to main, develop, or chapter-* branches
- Pull requests to main

## Test Scenarios

### Player Highlight Test
- Loads a sample recording (`examples/recordings/fizzbuzz.orirec`)
- Seeks to 0.8 (80%) on the timeline
- Asserts that a highlight ring exists on the expected block
- Verifies the highlight ring has correct styling (blue border)
- Checks that the current frame indicator shows the correct frame

## Test Data

The tests use the existing `fizzbuzz.orirec` recording file which contains:
- Multiple frames with different block types (LetNode, RepeatNode, SayNode)
- Local variables that change over time
- A timeline that can be seeked to different positions

## Debugging

If tests fail, check:
1. Screenshots in `test-results/` directory
2. Playwright report in `playwright-report/` directory
3. Console logs for any JavaScript errors
4. Network tab for failed requests

## Adding New Tests

1. Create a new `.spec.ts` file in this directory
2. Import `test` and `expect` from `@playwright/test`
3. Use `data-testid` attributes to select elements
4. Add appropriate waits and assertions
5. Update the CI workflow if needed 