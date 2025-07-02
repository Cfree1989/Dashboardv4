# Testing Strategy - Dashboard v4

This document outlines the comprehensive testing strategy for Dashboard v4, including test organization, patterns, and best practices.

## 📋 Testing Philosophy

Dashboard v4 follows a **Testing Pyramid** approach with emphasis on:
- **Test-Driven Development (TDD)** for new feature development
- **Accessibility-First Testing** using React Testing Library
- **User-Centric Testing** focusing on user interactions and workflows
- **AI Agent Optimization** with clear patterns and examples

## 🏗 Testing Architecture

### Testing Pyramid Structure
```
                    /\
                   /  \
                  / E2E \
                 /______\
                /        \
               /Integration\
              /__________\
             /              \
            /      Unit       \
           /________________\
```

**Ratios**: 70% Unit, 20% Integration, 10% E2E

### Directory Structure
```
tests/
├── README.md                    # This file - testing strategy and guidelines
├── config/                      # Testing configuration files
│   ├── jest.config.js          # Jest configuration
│   ├── playwright.config.ts    # Playwright E2E configuration
│   ├── test-utils.tsx          # Custom testing utilities
│   └── setup.ts                # Global test setup
├── unit/                        # Unit tests (70% of tests)
│   ├── components/             # Component unit tests
│   ├── hooks/                  # Custom hook tests
│   ├── utils/                  # Utility function tests
│   └── types/                  # Type validation tests
├── integration/                 # Integration tests (20% of tests)
│   ├── api/                    # API integration tests
│   ├── workflows/              # User workflow tests
│   └── state/                  # State management tests
├── e2e/                        # End-to-end tests (10% of tests)
│   ├── critical-paths/         # Core user journeys
│   ├── accessibility/          # A11y compliance tests
│   └── performance/            # Performance testing
├── fixtures/                   # Test data and mocks
│   ├── jobs.json              # Sample job data
│   ├── users.json             # Sample user data
│   └── api-responses/         # Mock API responses
└── __mocks__/                  # Module mocks
    ├── next-router.js         # Next.js router mock
    └── api-client.js          # API client mock
```

## 🧪 Testing Tools and Libraries

### Core Testing Stack
- **Jest**: Test runner and assertion library
- **React Testing Library**: Component testing with accessibility focus
- **Playwright**: Cross-browser E2E testing
- **MSW (Mock Service Worker)**: API mocking for integration tests
- **jest-axe**: Accessibility testing automation

### Supporting Tools
- **@testing-library/user-event**: Realistic user interaction simulation
- **@testing-library/jest-dom**: Custom Jest matchers for DOM testing
- **faker.js**: Test data generation
- **coverage**: Code coverage reporting

## 📝 Testing Standards and Patterns

### Unit Testing Guidelines
- **Test file naming**: `ComponentName.test.tsx` or `functionName.test.ts`
- **Test organization**: Describe blocks for components, describe nested functionality
- **Assertions**: Use specific, meaningful assertions
- **Mocking**: Mock external dependencies, keep internal logic pure

### Component Testing Pattern
```typescript
// Example: JobCard.test.tsx
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { JobCard } from '@/components/dashboard/job-card';
import { createMockJob } from '../fixtures/job-helpers';

describe('JobCard', () => {
  const mockProps = {
    job: createMockJob({ status: 'pending' }),
    onApprove: jest.fn(),
    onReject: jest.fn(),
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Rendering', () => {
    it('displays job title and status', () => {
      render(<JobCard {...mockProps} />);
      
      expect(screen.getByText(mockProps.job.title)).toBeInTheDocument();
      expect(screen.getByText('pending')).toBeInTheDocument();
    });

    it('shows action buttons for pending jobs', () => {
      render(<JobCard {...mockProps} />);
      
      expect(screen.getByRole('button', { name: /approve/i })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /reject/i })).toBeInTheDocument();
    });
  });

  describe('User Interactions', () => {
    it('calls onApprove when approve button is clicked', async () => {
      const user = userEvent.setup();
      render(<JobCard {...mockProps} />);
      
      const approveButton = screen.getByRole('button', { name: /approve/i });
      await user.click(approveButton);
      
      expect(mockProps.onApprove).toHaveBeenCalledWith(mockProps.job.id);
    });
  });

  describe('Accessibility', () => {
    it('meets accessibility standards', async () => {
      const { container } = render(<JobCard {...mockProps} />);
      
      const results = await axe(container);
      expect(results).toHaveNoViolations();
    });
  });
});
```

### Integration Testing Pattern
```typescript
// Example: job-workflow.test.tsx
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { setupServer } from 'msw/node';
import { rest } from 'msw';
import { Dashboard } from '@/components/dashboard/dashboard';

const server = setupServer(
  rest.get('/api/jobs', (req, res, ctx) => {
    return res(ctx.json({ jobs: [mockPendingJob] }));
  }),
  rest.post('/api/jobs/:id/approve', (req, res, ctx) => {
    return res(ctx.json({ success: true }));
  })
);

beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

describe('Job Approval Workflow', () => {
  it('completes job approval workflow successfully', async () => {
    const user = userEvent.setup();
    render(<Dashboard />);
    
    // Wait for jobs to load
    await waitFor(() => {
      expect(screen.getByText('Test Job')).toBeInTheDocument();
    });
    
    // Click approve button
    const approveButton = screen.getByRole('button', { name: /approve test job/i });
    await user.click(approveButton);
    
    // Confirm in modal
    const confirmButton = screen.getByRole('button', { name: /confirm/i });
    await user.click(confirmButton);
    
    // Verify success feedback
    await waitFor(() => {
      expect(screen.getByText(/job approved successfully/i)).toBeInTheDocument();
    });
  });
});
```

### E2E Testing Pattern
```typescript
// Example: critical-user-journeys.spec.ts
import { test, expect } from '@playwright/test';

test.describe('Job Management Dashboard', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/dashboard');
  });

  test('user can approve a job end-to-end', async ({ page }) => {
    // Navigate to pending jobs
    await page.click('button:has-text("Pending")');
    
    // Find and approve a job
    await page.click('[data-testid="job-card"]:first-child >> button:has-text("Approve")');
    
    // Fill approval modal
    await page.fill('[data-testid="approval-notes"]', 'Approved via E2E test');
    await page.click('button:has-text("Confirm")');
    
    // Verify success
    await expect(page.locator('.toast')).toContainText('Job approved successfully');
    
    // Verify job moved to approved tab
    await page.click('button:has-text("Approved")');
    await expect(page.locator('[data-testid="job-card"]')).toBeVisible();
  });

  test('dashboard is accessible via keyboard navigation', async ({ page }) => {
    // Test keyboard navigation
    await page.keyboard.press('Tab');
    await expect(page.locator(':focus')).toBeVisible();
    
    // Navigate through status tabs
    await page.keyboard.press('ArrowRight');
    await page.keyboard.press('Enter');
    
    // Verify tab activation
    await expect(page.locator('[aria-selected="true"]')).toBeVisible();
  });
});
```

## 🎯 Test Coverage Goals

### Coverage Targets
- **Overall Coverage**: >85%
- **Components**: >90%
- **Business Logic**: >95%
- **Critical Paths**: 100%

### Coverage Exclusions
- Configuration files
- Type definitions
- Mock files
- Build artifacts

## 🚀 Running Tests

### Available Commands
```bash
# Run all tests
npm test

# Run tests in watch mode
npm run test:watch

# Run specific test suite
npm run test:unit
npm run test:integration
npm run test:e2e

# Run tests with coverage
npm run test:coverage

# Run accessibility tests
npm run test:a11y

# Run performance tests
npm run test:performance
```

### CI/CD Integration
Tests run automatically on:
- **Pull Request Creation**: Full test suite
- **Push to Main**: Full test suite + E2E
- **Release**: Full test suite + performance + accessibility

## 📊 Quality Gates

### Pre-commit Checks
- [ ] All tests passing
- [ ] Coverage thresholds met
- [ ] No accessibility violations
- [ ] Performance benchmarks met

### Pre-merge Requirements
- [ ] Unit tests: >90% coverage
- [ ] Integration tests: All critical paths covered
- [ ] E2E tests: Core user journeys verified
- [ ] Accessibility: WCAG 2.1 AA compliance

## 🔧 Debugging and Troubleshooting

### Common Issues
1. **Flaky Tests**: Use `waitFor` for async operations
2. **Mock Issues**: Clear mocks between tests
3. **Timing Problems**: Use proper async/await patterns
4. **Accessibility Failures**: Check ARIA labels and semantic HTML

### Debug Utilities
```typescript
// Debug test rendering
import { debug } from '@testing-library/react';
render(<Component />);
debug(); // Prints DOM structure

// Debug specific element
debug(screen.getByRole('button'));

// Custom debug helper
export const debugComponent = (component: ReactElement) => {
  const { debug } = render(component);
  debug();
};
```

## 📈 Performance Testing

### Metrics to Track
- **Component Render Time**: <100ms for complex components
- **User Interaction Response**: <200ms
- **API Response Time**: <500ms
- **Bundle Size Impact**: Monitor test bundle growth

### Performance Test Example
```typescript
test('JobCard renders within performance budget', async () => {
  const start = performance.now();
  render(<JobCard job={complexJob} />);
  const end = performance.now();
  
  expect(end - start).toBeLessThan(100); // 100ms budget
});
```

## 🎯 Testing Best Practices

### Do's
- ✅ Test user behavior, not implementation details
- ✅ Use semantic queries (getByRole, getByLabelText)
- ✅ Test accessibility as a first-class concern
- ✅ Mock external dependencies
- ✅ Write descriptive test names
- ✅ Group related tests with describe blocks
- ✅ Use setup/teardown appropriately

### Don'ts
- ❌ Test internal component state directly
- ❌ Use querySelector for interactive elements
- ❌ Rely on brittle CSS selectors
- ❌ Mock React components unnecessarily
- ❌ Write tests that test mocks
- ❌ Ignore accessibility in tests
- ❌ Test multiple concerns in one test

## 🤖 AI Agent Testing Assistance

### Patterns for AI Agents
- **Consistent naming**: Follow established test file patterns
- **Standard structures**: Use describe/it blocks consistently
- **Mock patterns**: Reuse mock creation patterns
- **Assertion patterns**: Use semantic assertions
- **Setup patterns**: Follow beforeEach/afterEach conventions

### Test Generation Guidelines
When AI agents generate tests, ensure:
- Tests focus on user-facing behavior
- Accessibility testing is included
- Mock data follows realistic patterns
- Error scenarios are covered
- Performance considerations are included

---

This testing strategy ensures Dashboard v4 maintains high quality while supporting confident development and refactoring. All tests should focus on user value and accessibility while providing clear feedback for developers and AI agents. 