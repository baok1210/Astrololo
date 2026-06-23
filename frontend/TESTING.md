# Frontend Testing Setup

This project uses Vitest for testing React components.

## Setup

Install test dependencies:

```bash
cd frontend
npm install -D vitest @vitest/ui @testing-library/react @testing-library/jest-dom jsdom
```

## Test Structure

Create test files in `frontend/src/components/__tests__/`:

```
frontend/src/
  components/
    __tests__/
      ChartWheel.test.tsx
      InterpretationView.test.tsx
      NatalPanel.test.tsx
      AspectTable.test.tsx
```

## Running Tests

```bash
# Run tests in watch mode (recommended for development)
npm test

# Run tests once
npm run test:run

# Open UI test runner
npm run test:ui
```

## Test Examples

Here's a basic test structure to get started:

```tsx
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { describe, it, expect, vi } from 'vitest'
import NatalPanel from './NatalPanel'

describe('NatalPanel', () => {
  it('renders birth form', () => {
    render(<NatalPanel />)
    expect(screen.getByLabelText('Họ Tên *')).toBeInTheDocument()
    expect(screen.getByLabelText('Năm')).toBeInTheDocument()
    expect(screen.getByLabelText('Tháng')).toBeInTheDocument()
    expect(screen.getByLabelText('Ngày')).toBeInTheDocument()
  })

  it('shows validation error when name is empty', async () => {
    render(<NatalPanel />)
    const submitButton = screen.getByText('Tra cứu Lá Số')
    fireEvent.click(submitButton)
    
    await waitFor(() => {
      expect(screen.getByText('Vui lòng nhập họ tên.')).toBeInTheDocument()
    })
  })
})
```

## Tips

- Use `vi.mock` to mock API calls
- Use `await waitFor` for async operations
- Use `screen.debug()` to debug test failures
- Use `userEvent` for more realistic user interactions
