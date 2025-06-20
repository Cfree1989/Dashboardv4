# Contributing Guidelines

Thank you for considering contributing to the 3D Print System project. This document outlines the process and conventions to follow when contributing.

## Development Environment

1. **Prerequisites**
   - Docker and Docker Compose
   - Node.js 18+ (for frontend development)
   - Python 3.9+ (for backend development)
   - VSCode with Python and TypeScript extensions (recommended)

2. **Setup**
   - Fork and clone the repository
   - Run `docker-compose -f docker-compose.dev.yml up -d` to start development services
   - Frontend development server: `cd frontend && npm run dev`
   - Backend development server: `cd backend && flask run --debug`

## Branch Naming Convention

Use the following format for branch names:

- `feature/short-description` - For new features
- `bugfix/short-description` - For bug fixes
- `hotfix/short-description` - For critical production fixes
- `docs/short-description` - For documentation updates
- `refactor/short-description` - For code refactoring without behavior changes

Examples:
- `feature/email-notifications`
- `bugfix/file-path-validation`
- `docs/api-documentation`

## Commit Style Guidelines

Follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

Types:
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `style:` - Code style/formatting changes (no behavior change)
- `refactor:` - Code refactoring (no behavior change)
- `test:` - Adding/updating tests
- `chore:` - Build, tooling, dependency updates

Examples:
- `feat(dashboard): add sound notifications for new jobs`
- `fix(file-service): correct path validation error`
- `docs: update API specification for job approval endpoint`

## Pull Request Process

1. **Before Submitting**
   - Ensure code follows project conventions
   - Add appropriate tests for new functionality
   - Update documentation if necessary
   - Verify that all tests pass

2. **PR Description**
   - Use the provided PR template
   - Clearly describe the changes and their purpose
   - Reference any related issues with `#issue-number`
   - Include steps to test or verify changes

3. **Review Process**
   - PRs require at least one review before merging
   - Address all feedback from reviewers
   - Ensure CI passes before requesting review

## Code Conventions

### Backend (Flask)

- Follow [PEP 8](https://pep8.org/) style guide
- Use type hints for all functions and methods
- Document all public functions, classes, and methods
- Organize routes using Blueprint structure
- Handle errors gracefully with proper status codes
- Log significant events and errors

### Frontend (Next.js)

- Use TypeScript for all new components and files
- Follow the existing component organization
- Use shadcn/ui components for UI elements
- Implement proper prop validation
- Follow mobile-first responsive design
- Use React Context for shared state
- Format with Prettier (configuration in repo)

## Testing Guidelines

- Backend: Write unit tests with pytest
- Frontend: Write component tests with React Testing Library
- Cover critical paths and edge cases
- Mock external dependencies appropriately
- Test for accessibility and mobile responsiveness

## Documentation

- Update README.md when adding new features or changing existing ones
- Document API endpoints in the OpenAPI specification
- Add JSDoc comments for TypeScript components and functions
- Update architecture diagrams for significant changes 