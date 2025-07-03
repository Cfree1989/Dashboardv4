// Custom testing utilities for Dashboard v4
import React, { ReactElement, ReactNode } from 'react';
import { render, RenderOptions, RenderResult, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { axe } from 'jest-axe';
import type { Job, JobStatus } from '../../Project Information/v0/types/job';
import { DashboardProvider } from '../../Project Information/v0/components/dashboard/dashboard-context';

// Mock providers for testing
interface MockProvidersProps {
  children: ReactNode;
  initialDashboardState?: {
    jobs?: Job[];
    selectedFilter?: JobStatus | 'all';
    soundEnabled?: boolean;
  };
}

function MockProviders({ children, initialDashboardState = {} }: MockProvidersProps) {
  // Use the real DashboardProvider with mock initial state
  const mockJobs = initialDashboardState.jobs || [];
  
  return (
    <DashboardProvider>
      {children}
    </DashboardProvider>
  );
}

// Custom render function with providers
interface CustomRenderOptions extends Omit<RenderOptions, 'wrapper'> {
  initialState?: {
    jobs?: Job[];
    selectedFilter?: JobStatus | 'all';
    soundEnabled?: boolean;
  };
}

export function renderWithProviders(
  ui: ReactElement,
  options: CustomRenderOptions = {}
): RenderResult & { user: ReturnType<typeof userEvent.setup> } {
  const { initialState, ...renderOptions } = options;

  const Wrapper = ({ children }: { children: ReactNode }) => (
    <MockProviders initialDashboardState={initialState}>
      {children}
    </MockProviders>
  );

  const result = render(ui, { wrapper: Wrapper, ...renderOptions });
  
  return {
    ...result,
    user: userEvent.setup(),
  };
}

// Re-export everything from React Testing Library
export * from '@testing-library/react';
export { userEvent };

// Custom render as default export for convenience
export { renderWithProviders as render };

// Helper functions for creating test data
export const createMockJob = (overrides: Partial<Job> = {}): Job => ({
  id: `job-${Math.random().toString(36).substr(2, 9)}`,
  studentName: 'Test Student',
  studentEmail: 'test@example.com',
  discipline: 'Engineering',
  classNumber: 'ENG101',
  originalFilename: 'test-file.stl',
  displayName: 'Test Job Title',
  filePath: '/path/to/test-file.stl',
  metadataPath: '/path/to/test-metadata.json',
  status: 'UPLOADED',
  printer: 'Printer A',
  color: 'PLA Black',
  material: 'PLA',
  weightG: 25.5,
  timeHours: 2.5,
  costUsd: 5.75,
  createdAt: new Date('2024-01-15T10:00:00Z').toISOString(),
  updatedAt: new Date('2024-01-15T10:00:00Z').toISOString(),
  staffViewedAt: null,
  notes: null,
  ...overrides,
});

export const createMockJobs = (count: number = 5): Job[] => {
  const statuses: JobStatus[] = ['UPLOADED', 'PENDING', 'READYTOPRINT', 'PRINTING', 'COMPLETED'];
  
  return Array.from({ length: count }, (_, index) => createMockJob({
    id: `job-${index + 1}`,
    studentName: `Test Student ${index + 1}`,
    displayName: `Test Job ${index + 1}`,
    status: statuses[index % statuses.length],
    createdAt: new Date(Date.now() - (index * 86400000)).toISOString(), // Spread over days
  }));
};

// Accessibility testing helpers
export const testAccessibility = async (container: Element): Promise<void> => {
  const results = await axe(container);
  expect(results).toHaveNoViolations();
};

export const testKeyboardNavigation = async (
  element: Element,
  expectedFocusOrder: string[]
): Promise<void> => {
  const user = userEvent.setup();
  
  // Focus the first element
  (element as HTMLElement).focus();
  
  for (let i = 0; i < expectedFocusOrder.length; i++) {
    await user.keyboard('[Tab]');
    const focusedElement = document.activeElement;
    
    if (expectedFocusOrder[i]) {
      expect(focusedElement).toHaveAttribute('data-testid', expectedFocusOrder[i]);
    }
  }
};

// API mocking helpers
export const mockApiResponse = <T,>(data: T, delay = 0): Promise<T> => {
  return new Promise((resolve) => {
    setTimeout(() => resolve(data), delay);
  });
};

export const mockApiError = (message = 'API Error', status = 500): Promise<never> => {
  return Promise.reject(new Error(`${status}: ${message}`));
};

// Custom matchers for common assertions
export const expectJobCard = (container: Element, job: Job) => {
  expect(container).toHaveTextContent(job.displayName);
  expect(container).toHaveTextContent(job.status);
  expect(container).toHaveTextContent(job.studentName);
};

export const expectModalToBeOpen = (modalTitle: string) => {
  const modal = document.querySelector('[role="dialog"]');
  expect(modal).toBeInTheDocument();
  expect(modal).toHaveTextContent(modalTitle);
};

export const expectModalToBeClosed = () => {
  const modal = document.querySelector('[role="dialog"]');
  expect(modal).not.toBeInTheDocument();
};

// Performance testing helpers
export const measureRenderTime = async (renderFn: () => RenderResult): Promise<number> => {
  const start = performance.now();
  renderFn();
  const end = performance.now();
  return end - start;
};

export const expectRenderWithinBudget = async (
  renderFn: () => RenderResult,
  budgetMs: number
): Promise<void> => {
  const renderTime = await measureRenderTime(renderFn);
  expect(renderTime).toBeLessThan(budgetMs);
};

// Form testing helpers
export const fillFormField = async (
  user: ReturnType<typeof userEvent.setup>,
  labelText: string,
  value: string
): Promise<void> => {
  const field = document.querySelector(`[aria-label="${labelText}"], [placeholder*="${labelText}"]`) as HTMLElement;
  if (!field) {
    throw new Error(`Could not find form field with label: ${labelText}`);
  }
  
  await user.clear(field);
  await user.type(field, value);
};

export const submitForm = async (
  user: ReturnType<typeof userEvent.setup>,
  formTestId?: string
): Promise<void> => {
  const submitButton = formTestId
    ? document.querySelector(`[data-testid="${formTestId}"] button[type="submit"]`)
    : document.querySelector('button[type="submit"]');
    
  if (!submitButton) {
    throw new Error('Could not find submit button');
  }
  
  await user.click(submitButton as HTMLElement);
};

// Local storage testing helpers
export const mockLocalStorage = (initialData: Record<string, string> = {}) => {
  const storage: Record<string, string> = { ...initialData };
  
  return {
    getItem: jest.fn((key: string) => storage[key] || null),
    setItem: jest.fn((key: string, value: string) => {
      storage[key] = value;
    }),
    removeItem: jest.fn((key: string) => {
      delete storage[key];
    }),
    clear: jest.fn(() => {
      Object.keys(storage).forEach(key => delete storage[key]);
    }),
    get length() {
      return Object.keys(storage).length;
    },
    key: jest.fn((index: number) => Object.keys(storage)[index] || null),
  };
};

// Wait for async operations
export const waitForLoadingToFinish = async () => {
  const loadingSpinner = document.querySelector('[data-testid="loading-spinner"]');
  if (loadingSpinner) {
    await waitFor(() => {
      expect(loadingSpinner).not.toBeInTheDocument();
    });
  }
};

// Custom hooks testing helper
export const renderHook = <T,>(hook: () => T): { result: { current: T }; rerender: () => void } => {
  let result: { current: T };
  
  function TestComponent() {
    result = { current: hook() };
    return null;
  }
  
  const { rerender: rerenderComponent } = render(<TestComponent />);
  
  return {
    result: result!,
    rerender: () => rerenderComponent(<TestComponent />),
  };
};

// Debug helpers for troubleshooting tests
export const debugElement = (element: Element | null, message = '') => {
  if (message) console.log(`DEBUG: ${message}`);
  if (element) {
    console.log('Element:', element);
    console.log('innerHTML:', element.innerHTML);
    console.log('Attributes:', Array.from(element.attributes).map(attr => `${attr.name}="${attr.value}"`));
  } else {
    console.log('Element not found');
  }
};

export const debugDocument = (selector?: string) => {
  if (selector) {
    const elements = document.querySelectorAll(selector);
    console.log(`Found ${elements.length} elements matching "${selector}"`);
    elements.forEach((el, index) => {
      console.log(`Element ${index + 1}:`, el);
    });
  } else {
    console.log('Document body:', document.body.innerHTML);
  }
};

// Wait utilities
export { waitFor, waitForElementToBeRemoved } from '@testing-library/react'; 