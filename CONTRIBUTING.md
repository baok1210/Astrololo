# Contributing Guide

Thank you for your interest in contributing to Astrololo! This guide will help you get started and ensure your contributions align with our project goals and coding standards.

## Table of Contents

1. [General Guidelines](#general-guidelines)
2. [Code Style](#code-style)
3. [Testing](#testing)
4. [Documentation](#documentation)
5. [Version Control](#version-control)
6. [Feature Requests and Bug Reports](#feature-requests-and-bug-reports)

## General Guidelines

### Before You Start

1. **Fork the repository**: Create your own fork of the Astrololo repository on GitHub.
2. **Set up your development environment**: Follow the [quick start guide](#quick-start) to set up the development environment.
3. **Run tests**: Ensure all tests pass before making any changes.
4. **Create a branch**: Work on a feature branch rather than master.

### Workflow

1. **Branch naming**: Use descriptive branch names like:
   - `feature/name-of-feature`
   - `bugfix/name-of-bugfix`
   - `docs/additional-documentation`

2. **Pull requests**: Submit pull requests to the `main` branch for review.
3. **Code review**: Be prepared for feedback and iterate as needed.

## Code Style

### Python Backend

- **Type hints**: Use Python type hints for better code clarity.
- **Line length**: Keep lines under 100 characters.
- **Docstrings**: Include docstrings for public functions and classes.
- **Imports**: Organize imports using standard conventions.
- **Error handling**: Use `try-except` blocks with specific exceptions rather than bare `except:` clauses.
- **Logging**: Use the `logger` object for all logging needs (see `backend/astrololo/api/main.py` for examples).

### JavaScript/TypeScript Frontend

- **TypeScript**: Use TypeScript throughout. Ensure all components have proper type definitions.
- **Prop drilling**: Minimize prop drilling by using context providers or state management libraries if needed.
- **Component composition**: Build reusable, composable components.
- **Error boundaries**: Ensure all components are wrapped in error boundaries.
- **React hooks**: Follow React hook rules (e.g., no conditional hooks).

### Code Quality

- **Avoid code duplication**: Extract common functionality into reusable modules.
- **Performance**: Optimize for performance, especially in chart rendering and data processing.
- **Accessibility**: Ensure UI components are accessible.

## Testing

### Backend Tests

Run the comprehensive backtest suite:

```bash
cd backend
python -m backend.tests.backtest
```

This runs 144 tests covering:
- Core constants
- Ephemeris calculations
- Aspect calculations
- Chart construction
- Interpretation quality
- English interpretation
- YAML template coverage
- Pattern detection
- Scoring
- Edge cases

### Frontend Tests

The frontend currently does not have automated tests. Consider contributing test setup:

```bash
cd frontend
npm install -D jest @testing-library/react @testing-library/jest-dom
```

And add a `frontend/src/components/__tests__/` directory for component tests.

### Linting and Type Checking

Run the following commands to ensure code quality:

**Python:**
```bash
cd backend
ruff check .
```

**TypeScript:**
```bash
cd frontend
npx tsc --noEmit
```

## Documentation

### Code Documentation

- Add docstrings for all public Python functions and classes.
- Add TypeDoc comments for JavaScript/TypeScript interfaces and types.
- Update README with new features and changes.

### User Documentation

- Update the [main README.md](README.md) with new information.
- Consider creating additional documentation for complex features.

## Version Control

### Commit Message Guidelines

- Follow conventional commit format:
  - `feat: add new feature`
  - `fix: resolve specific bug`
  - `docs: update documentation`
  - `style: formatting or code style changes`
  - `refactor: code refactoring without bug fixes`
  - `test: add or modify tests`
  - `chore: maintenance tasks`

### Branch Strategy

- `main` branch: Production-ready code
- Feature branches: Work on new features or bug fixes
- `develop` branch: Integration branch (if used)

## Feature Requests and Bug Reports

### Feature Requests

1. Open an issue with the `feature` label.
2. Describe the use case and why it's needed.
3. Consider proposing an implementation approach.

### Bug Reports

1. Open an issue with the `bug` label.
2. Include reproduction steps and expected vs. actual behavior.
3. If possible, include a test case that reproduces the issue.

## Security Considerations

When contributing code:

1. Never commit secrets or API keys to the repository.
2. Use environment variables for sensitive configuration.
3. Validate user input thoroughly.
4. Consider potential DoS attacks (rate limiting, etc.).

## Code of Conduct

By contributing to Astrololo, you agree to:

1. Be respectful and inclusive.
2. Treat all participants with dignity and respect.
3. Follow the project's code of conduct.

## Acknowledgment

Thank you for considering contributing to Astrololo! Your contributions help make this project better for everyone.

## License

[MIT License](LICENSE)
