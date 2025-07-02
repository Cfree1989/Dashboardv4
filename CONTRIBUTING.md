# Contributing to Dashboard v4

Thank you for your interest in contributing to Dashboard v4! This document outlines the development workflow, coding standards, and contribution guidelines.

## 📋 Table of Contents

- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Branch Naming](#branch-naming)
- [Commit Guidelines](#commit-guidelines)
- [Pull Request Process](#pull-request-process)
- [Code Standards](#code-standards)
- [Testing Requirements](#testing-requirements)
- [AI Agent Guidelines](#ai-agent-guidelines)

## 🚀 Getting Started

### Prerequisites
- Node.js 18+ 
- pnpm (recommended package manager)
- Git
- VS Code (recommended IDE)

### Initial Setup
```bash
# Clone the repository
git clone <repository-url>
cd Dashboardv4

# Install dependencies
cd v0
pnpm install

# Start development server
pnpm dev
```

### Project Structure Familiarization
- Read [`README.md`](./README.md) for project overview
- Review [`project-info.md`](./project-info.md) for domain context
- Check [`CURSOR.md`](./CURSOR.md) for AI agent optimization tips

## 🔄 Development Workflow

### 1. Before Starting Work
```bash
# Ensure you're on the latest main branch
git checkout master
git pull origin master

# Create a new feature branch
git checkout -b feature/your-feature-name
```

### 2. During Development
```bash
# Navigate to application directory
cd v0

# Start development server
pnpm dev

# Run type checking frequently
pnpm type-check

# Run linting
pnpm lint
```

### 3. Before Committing
```bash
# Run full check suite
pnpm type-check
pnpm lint
pnpm test (when tests are available)

# Stage and commit changes
git add .
git commit -m "feat(component): add job approval modal"
```

## 🌟 Branch Naming

### Branch Naming Convention
Use the following format: `<type>/<short-description>`

### Types
- **feature/** - New features or enhancements
- **fix/** - Bug fixes
- **docs/** - Documentation updates
- **style/** - Code style/formatting changes
- **refactor/** - Code refactoring without changing functionality
- **test/** - Adding or updating tests
- **chore/** - Maintenance tasks

### Examples
```bash
feature/job-approval-modal
fix/status-tab-navigation
docs/update-readme
style/component-formatting
refactor/dashboard-context
test/job-card-component
chore/update-dependencies
```

### Branch Naming Rules
- Use lowercase letters
- Use hyphens (-) to separate words
- Keep descriptions concise but descriptive
- Avoid special characters except hyphens
- Maximum 50 characters

## 📝 Commit Guidelines

### Commit Message Format
```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

### Types
- **feat**: New feature
- **fix**: Bug fix
- **docs**: Documentation changes
- **style**: Code style changes (formatting, missing semicolons, etc.)
- **refactor**: Code refactoring
- **test**: Adding or updating tests
- **chore**: Maintenance tasks

### Scopes
- **dashboard**: Dashboard-specific components
- **components**: UI components
- **types**: TypeScript type definitions
- **hooks**: Custom React hooks
- **utils**: Utility functions
- **config**: Configuration files
- **docs**: Documentation

### Examples
```bash
feat(dashboard): add job approval modal with confirmation dialog
fix(components): resolve JobCard status display issue
docs(readme): update installation instructions
style(dashboard): format component code with prettier
refactor(hooks): optimize useJobData performance
test(components): add JobCard component tests
chore(deps): update Next.js to latest version
```

### Commit Message Rules
- Use present tense ("add feature" not "added feature")
- Use imperative mood ("move cursor to..." not "moves cursor to...")
- First line should be 50 characters or less
- Reference issues and pull requests when applicable
- Body should explain what and why, not how

## 🔀 Pull Request Process

### 1. Before Creating PR
- [ ] Code follows project conventions
- [ ] All tests pass (when available)
- [ ] TypeScript compilation successful
- [ ] Linting passes without errors
- [ ] Documentation updated if necessary

### 2. Creating the Pull Request

#### PR Title Format
Use the same format as commit messages:
```
<type>(<scope>): <description>
```

#### PR Description Template
```markdown
## Description
Brief description of changes made.

## Type of Change
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## Testing
- [ ] I have tested these changes locally
- [ ] TypeScript compilation passes
- [ ] Linting passes without errors
- [ ] Manual testing completed

## Screenshots (if applicable)
Include screenshots of UI changes.

## Checklist
- [ ] My code follows the style guidelines of this project
- [ ] I have performed a self-review of my own code
- [ ] I have commented my code, particularly in hard-to-understand areas
- [ ] I have made corresponding changes to the documentation
- [ ] My changes generate no new warnings
```

### 3. Review Process
- **At least one approval** required before merging
- **Address all review comments** before final approval
- **Squash commits** if requested by reviewers
- **Update branch** if conflicts arise

### 4. Merging Guidelines
- Use **Squash and Merge** for feature branches
- Use **Merge Commit** for release branches
- Delete branch after successful merge

## 💻 Code Standards

### TypeScript Requirements
- **Strict mode enabled** - no `any` types without justification
- **Explicit return types** for all functions
- **Interface definitions** for all component props
- **Type exports** from appropriate files

```typescript
// ✅ Good
interface JobCardProps {
  job: Job;
  onUpdate: (job: Job) => void;
  isSelected?: boolean;
}

export function JobCard({ job, onUpdate, isSelected = false }: JobCardProps): JSX.Element {
  // Implementation
}

// ❌ Bad
export function JobCard({ job, onUpdate, isSelected }) {
  // Missing types
}
```

### React Best Practices
- **Functional components** with hooks (no class components)
- **Proper hook usage** - follow rules of hooks
- **Component composition** over inheritance
- **Prop drilling avoidance** - use context when appropriate

### Styling Guidelines
- **Tailwind CSS** for styling (no inline styles)
- **Consistent spacing** using Tailwind scale
- **Responsive design** patterns
- **Semantic class names** when custom CSS is needed

```tsx
// ✅ Good
<div className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
  <span className="text-sm font-medium text-gray-900">{job.title}</span>
</div>

// ❌ Bad
<div style={{ display: 'flex', padding: '16px' }}>
  <span style={{ fontSize: '14px' }}>{job.title}</span>
</div>
```

### File Organization
- **Consistent naming** - PascalCase for components, camelCase for utilities
- **Proper imports** - absolute imports for project files
- **Barrel exports** - use index.ts files for clean imports
- **Colocation** - keep related files together

## 🧪 Testing Requirements

### Testing Strategy (Future Implementation)
- **Unit tests** for utility functions
- **Component tests** for React components
- **Integration tests** for complex workflows
- **E2E tests** for critical user paths

### Testing Guidelines
```typescript
// Example component test structure
describe('JobCard', () => {
  it('renders job information correctly', () => {
    // Test implementation
  });

  it('handles status updates', () => {
    // Test implementation
  });
});
```

### Coverage Requirements
- **80% minimum** code coverage (when implemented)
- **Critical paths** must be tested
- **Edge cases** should be covered
- **Error scenarios** must be tested

## 🤖 AI Agent Guidelines

### For AI-Assisted Development
- **Always reference** [`project-info.md`](./project-info.md) for domain context
- **Follow established patterns** in existing components
- **Use existing types** from `v0/types/` directory
- **Maintain consistency** with current code style

### AI Code Review Checklist
- [ ] Types are properly defined
- [ ] Component follows existing patterns
- [ ] Imports are organized correctly
- [ ] Error handling is implemented
- [ ] Accessibility considerations addressed
- [ ] Performance optimizations applied where needed

### Communication Guidelines
- **Be specific** about file paths and component names
- **Reference existing code** when explaining patterns
- **Include type information** in code examples
- **Explain business context** for complex changes

## 📞 Getting Help

### Resources
- **Project Documentation**: Start with [`README.md`](./README.md)
- **AI Agent Tips**: Check [`CURSOR.md`](./CURSOR.md)
- **Domain Context**: Review [`project-info.md`](./project-info.md)

### Common Issues
- **Build errors**: Run `pnpm type-check` and `pnpm lint`
- **Import issues**: Check file paths and exports
- **Styling problems**: Verify Tailwind class names
- **Type errors**: Review TypeScript interfaces

### Best Practices for Questions
1. **Search existing issues** first
2. **Provide context** about what you're trying to achieve
3. **Include error messages** and stack traces
4. **Share relevant code snippets**
5. **Mention your environment** (Node version, OS, etc.)

## 🎯 Quality Checklist

Before submitting any contribution, ensure:

### Code Quality
- [ ] TypeScript strict mode compliance
- [ ] ESLint rules followed
- [ ] Prettier formatting applied
- [ ] No console.log statements in production code
- [ ] Error handling implemented
- [ ] Performance considerations addressed

### Documentation
- [ ] Code is self-documenting with clear names
- [ ] Complex logic has explanatory comments
- [ ] README updated if necessary
- [ ] Type definitions are comprehensive

### Testing
- [ ] Manual testing completed
- [ ] Edge cases considered
- [ ] Error scenarios tested
- [ ] Responsive design verified

Thank you for contributing to Dashboard v4! Your efforts help make this project better for everyone, including AI coding agents that work with this codebase. 