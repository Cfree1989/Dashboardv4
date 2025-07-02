# Style Guide - Dashboard v4

This document defines the comprehensive style standards for the Dashboard v4 project, covering code style, design patterns, and UI/UX guidelines to ensure consistency across all development work.

## 📖 Overview

The Dashboard v4 style guide ensures:
- **Consistency** across all code and design elements
- **Maintainability** through standardized patterns
- **Accessibility** compliance with WCAG 2.1 AA standards
- **AI Agent Effectiveness** through predictable patterns and naming conventions
- **Team Collaboration** with shared understanding of standards

---

## 🎨 Design System

### Color Palette

#### Primary Colors
```css
/* Primary Brand Colors */
--primary-50: #eff6ff;
--primary-100: #dbeafe;
--primary-500: #3b82f6;    /* Main brand blue */
--primary-600: #2563eb;
--primary-700: #1d4ed8;
--primary-900: #1e3a8a;
```

#### Status Colors
```css
/* Job Status Colors */
--status-pending: #f59e0b;     /* Amber - pending jobs */
--status-approved: #10b981;    /* Green - approved jobs */
--status-rejected: #ef4444;    /* Red - rejected jobs */
--status-completed: #6b7280;   /* Gray - completed jobs */
```

#### Neutral Colors
```css
/* Gray Scale */
--gray-50: #f9fafb;
--gray-100: #f3f4f6;
--gray-200: #e5e7eb;
--gray-300: #d1d5db;
--gray-500: #6b7280;
--gray-700: #374151;
--gray-900: #111827;
```

#### Usage Guidelines
- **Primary colors** for interactive elements (buttons, links, focus states)
- **Status colors** for job state indicators and badges
- **Neutral colors** for text, backgrounds, and borders
- **Consistent contrast ratios** minimum 4.5:1 for normal text, 3:1 for large text

### Typography

#### Font Stack
```css
/* Primary Font Family */
font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
```

#### Type Scale
```css
/* Heading Sizes */
--text-xs: 0.75rem;    /* 12px */
--text-sm: 0.875rem;   /* 14px */
--text-base: 1rem;     /* 16px */
--text-lg: 1.125rem;   /* 18px */
--text-xl: 1.25rem;    /* 20px */
--text-2xl: 1.5rem;    /* 24px */
--text-3xl: 1.875rem;  /* 30px */
--text-4xl: 2.25rem;   /* 36px */
```

#### Font Weights
```css
--font-normal: 400;
--font-medium: 500;
--font-semibold: 600;
--font-bold: 700;
```

#### Typography Guidelines
- **Headings**: Use semibold (600) or bold (700) weights
- **Body text**: Use normal (400) weight for readability
- **UI elements**: Use medium (500) for buttons and labels
- **Line height**: 1.5 for body text, 1.2 for headings
- **Letter spacing**: Default for most text, slight tracking for all-caps labels

### Spacing System

#### Base Unit
```css
/* 4px base unit for consistent spacing */
--space-1: 0.25rem;  /* 4px */
--space-2: 0.5rem;   /* 8px */
--space-3: 0.75rem;  /* 12px */
--space-4: 1rem;     /* 16px */
--space-5: 1.25rem;  /* 20px */
--space-6: 1.5rem;   /* 24px */
--space-8: 2rem;     /* 32px */
--space-10: 2.5rem;  /* 40px */
--space-12: 3rem;    /* 48px */
--space-16: 4rem;    /* 64px */
```

#### Usage Guidelines
- **Component padding**: Use space-4 (16px) as default
- **Element margins**: Use space-2 (8px) to space-6 (24px) for most cases
- **Section spacing**: Use space-8 (32px) or space-12 (48px) for major sections
- **Consistent application**: Stick to the defined scale for all spacing decisions

---

## 💻 Code Style Standards

### TypeScript Guidelines

#### Type Definitions
```typescript
// ✅ GOOD: Explicit interface definitions
interface JobCardProps {
  job: Job;
  onApprove: (jobId: string) => void;
  onReject: (jobId: string, reason: string) => void;
  isSelected?: boolean;
}

// ❌ BAD: Missing type definitions
function JobCard({ job, onApprove, onReject, isSelected }) {
  // Implementation
}
```

#### Naming Conventions
```typescript
// ✅ GOOD: Clear, descriptive naming
interface UserPreferences {
  soundEnabled: boolean;
  defaultFilter: JobStatus;
  notificationSettings: NotificationConfig;
}

// ❌ BAD: Abbreviated or unclear naming
interface UserPrefs {
  sound: boolean;
  filter: string;
  notifs: any;
}
```

#### Import Organization
```typescript
// ✅ GOOD: Organized imports
// 1. React imports
import React, { useState, useEffect } from 'react';

// 2. Third-party libraries
import { cn } from '@/lib/utils';

// 3. Internal components
import { Button } from '@/components/ui/button';
import { JobCard } from '@/components/dashboard/job-card';

// 4. Types and utilities
import type { Job, JobStatus } from '@/types/job';
import { formatDate } from '@/lib/date-utils';
```

### React Component Standards

#### Component Structure
```typescript
// ✅ GOOD: Standard component structure
interface ComponentProps {
  // Props interface
}

export function ComponentName({ prop1, prop2 }: ComponentProps) {
  // 1. Hooks (useState, useEffect, custom hooks)
  const [state, setState] = useState<StateType>();
  const customData = useCustomHook();
  
  // 2. Derived state and computations
  const computedValue = useMemo(() => {
    return calculateValue(state);
  }, [state]);
  
  // 3. Event handlers
  const handleAction = useCallback((param: string) => {
    // Handler logic
  }, [dependencies]);
  
  // 4. Effects
  useEffect(() => {
    // Effect logic
  }, [dependencies]);
  
  // 5. Early returns (loading, error states)
  if (loading) return <LoadingSpinner />;
  if (error) return <ErrorMessage error={error} />;
  
  // 6. Main render
  return (
    <div className="component-classes">
      {/* JSX content */}
    </div>
  );
}
```

#### Hook Usage Guidelines
```typescript
// ✅ GOOD: Custom hook for reusable logic
export function useJobActions() {
  const [loading, setLoading] = useState(false);
  
  const approveJob = useCallback(async (jobId: string, notes?: string) => {
    setLoading(true);
    try {
      await jobService.approve(jobId, notes);
      // Success handling
    } catch (error) {
      // Error handling
    } finally {
      setLoading(false);
    }
  }, []);
  
  return { approveJob, loading };
}

// ✅ GOOD: Using the custom hook
function JobCard({ job }: JobCardProps) {
  const { approveJob, loading } = useJobActions();
  
  const handleApprove = () => {
    approveJob(job.id);
  };
  
  // Component render
}
```

### CSS and Styling Guidelines

#### Tailwind CSS Best Practices
```jsx
// ✅ GOOD: Logical class ordering and responsive design
<div className="flex items-center justify-between p-4 border border-gray-200 rounded-lg bg-white shadow-sm hover:shadow-md transition-shadow duration-200 sm:p-6">
  <span className="text-sm font-medium text-gray-900 sm:text-base">
    {job.title}
  </span>
</div>

// ❌ BAD: Random class order and unclear intentions
<div className="border-gray-200 transition-shadow hover:shadow-md p-4 rounded-lg shadow-sm border bg-white duration-200 justify-between flex items-center">
  <span className="font-medium text-gray-900 text-sm">
    {job.title}
  </span>
</div>
```

#### Class Name Organization
1. **Layout**: flex, grid, block, inline
2. **Positioning**: relative, absolute, static
3. **Sizing**: w-*, h-*, max-w-*, min-h-*
4. **Spacing**: m-*, p-*, space-*
5. **Typography**: text-*, font-*, leading-*
6. **Colors**: text-*, bg-*, border-*
7. **Effects**: shadow-*, opacity-*, transform
8. **Interactions**: hover:*, focus:*, active:*
9. **Responsive**: sm:*, md:*, lg:*, xl:*

#### Custom CSS Guidelines
```css
/* ✅ GOOD: When Tailwind isn't sufficient */
.custom-component {
  /* Use CSS custom properties for dynamic values */
  background: linear-gradient(
    135deg,
    var(--primary-500) 0%,
    var(--primary-600) 100%
  );
  
  /* Follow BEM-like naming for complex components */
  &__element {
    /* Element styles */
  }
  
  &--modifier {
    /* Modifier styles */
  }
}

/* ❌ BAD: Avoid when Tailwind classes suffice */
.button {
  padding: 0.5rem 1rem;
  border-radius: 0.375rem;
  background-color: #3b82f6;
}
```

---

## 🎛 Component Design Patterns

### Job Card Component Pattern
```typescript
// Standard job card structure
interface JobCardProps {
  job: Job;
  onApprove?: (jobId: string) => void;
  onReject?: (jobId: string, reason: string) => void;
  showActions?: boolean;
  compact?: boolean;
}

export function JobCard({ 
  job, 
  onApprove, 
  onReject, 
  showActions = true,
  compact = false 
}: JobCardProps) {
  return (
    <Card className={cn(
      "transition-all duration-200 hover:shadow-md",
      compact && "p-3",
      !compact && "p-4"
    )}>
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between">
          <CardTitle className="text-lg">{job.title}</CardTitle>
          <JobStatusBadge status={job.status} />
        </div>
      </CardHeader>
      
      <CardContent>
        <div className="space-y-2">
          <JobPriority priority={job.priority} />
          <JobTimestamp createdAt={job.createdAt} />
        </div>
      </CardContent>
      
      {showActions && (
        <CardFooter className="pt-2">
          <JobActions 
            job={job}
            onApprove={onApprove}
            onReject={onReject}
          />
        </CardFooter>
      )}
    </Card>
  );
}
```

### Modal Component Pattern
```typescript
// Standard modal structure for job actions
interface JobActionModalProps {
  job: Job;
  isOpen: boolean;
  onClose: () => void;
  onConfirm: (data: ActionData) => void;
  title: string;
  children: React.ReactNode;
}

export function JobActionModal({
  job,
  isOpen,
  onClose,
  onConfirm,
  title,
  children
}: JobActionModalProps) {
  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>{title}</DialogTitle>
          <DialogDescription>
            Job: {job.title}
          </DialogDescription>
        </DialogHeader>
        
        <div className="py-4">
          {children}
        </div>
        
        <DialogFooter>
          <Button variant="outline" onClick={onClose}>
            Cancel
          </Button>
          <Button onClick={() => onConfirm(data)}>
            Confirm
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
```

### Form Input Pattern
```typescript
// Standard form input with validation
interface FormInputProps {
  label: string;
  error?: string;
  required?: boolean;
  children: React.ReactNode;
}

export function FormInput({ 
  label, 
  error, 
  required = false, 
  children 
}: FormInputProps) {
  return (
    <div className="space-y-2">
      <Label className="text-sm font-medium">
        {label}
        {required && <span className="text-red-500 ml-1">*</span>}
      </Label>
      
      {children}
      
      {error && (
        <p className="text-sm text-red-600" role="alert">
          {error}
        </p>
      )}
    </div>
  );
}
```

---

## 🔤 Naming Conventions

### File and Directory Naming
```
✅ GOOD Examples:
- components/JobCard.tsx
- components/dashboard/StatusTabs.tsx
- hooks/useJobData.ts
- types/Job.ts
- utils/formatDate.ts
- pages/dashboard/page.tsx

❌ BAD Examples:
- components/jobcard.tsx
- components/Dashboard_StatusTabs.tsx
- hooks/jobData.ts
- types/job-types.ts
- utils/date_utils.ts
```

### Variable and Function Naming
```typescript
// ✅ GOOD: Descriptive, intention-revealing names
const approvedJobsCount = jobs.filter(job => job.status === 'approved').length;
const handleJobApproval = (jobId: string) => { /* logic */ };
const isJobPending = (job: Job): boolean => job.status === 'pending';

// ❌ BAD: Abbreviated or unclear names
const count = jobs.filter(j => j.status === 'approved').length;
const handle = (id: string) => { /* logic */ };
const check = (job: Job): boolean => job.status === 'pending';
```

### Component and Interface Naming
```typescript
// ✅ GOOD: Clear, descriptive names
interface JobCardProps {
  job: Job;
  onApprove: (jobId: string) => void;
}

interface DashboardState {
  jobs: Job[];
  selectedFilter: JobStatus;
  isLoading: boolean;
}

// ❌ BAD: Generic or unclear names
interface Props {
  data: any;
  callback: Function;
}

interface State {
  items: any[];
  filter: string;
  loading: boolean;
}
```

---

## 📱 Responsive Design Guidelines

### Breakpoint Strategy
```css
/* Mobile First Approach */
.component {
  /* Mobile styles (320px+) */
  padding: 1rem;
  
  /* Tablet styles (768px+) */
  @media (min-width: 768px) {
    padding: 1.5rem;
  }
  
  /* Desktop styles (1024px+) */
  @media (min-width: 1024px) {
    padding: 2rem;
  }
  
  /* Large desktop (1280px+) */
  @media (min-width: 1280px) {
    padding: 2.5rem;
  }
}
```

### Component Responsiveness
```jsx
// ✅ GOOD: Responsive component design
<div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
  {jobs.map(job => (
    <JobCard 
      key={job.id} 
      job={job}
      compact={isMobile}
    />
  ))}
</div>

// Navigation responsive pattern
<nav className="flex flex-col space-y-2 sm:flex-row sm:space-y-0 sm:space-x-4">
  <StatusTab active>All Jobs</StatusTab>
  <StatusTab>Pending</StatusTab>
  <StatusTab>Approved</StatusTab>
</nav>
```

---

## ♿ Accessibility Standards

### ARIA Labels and Roles
```jsx
// ✅ GOOD: Proper ARIA implementation
<button
  aria-label={`Approve job ${job.title}`}
  aria-describedby={`job-${job.id}-description`}
  onClick={() => onApprove(job.id)}
>
  <CheckIcon className="w-4 h-4" aria-hidden="true" />
  Approve
</button>

<div 
  id={`job-${job.id}-description`}
  className="sr-only"
>
  {job.description}
</div>
```

### Keyboard Navigation
```typescript
// ✅ GOOD: Keyboard event handling
const handleKeyDown = (event: KeyboardEvent<HTMLDivElement>) => {
  switch (event.key) {
    case 'Enter':
    case ' ':
      event.preventDefault();
      onSelect();
      break;
    case 'Escape':
      onClose();
      break;
    case 'ArrowUp':
    case 'ArrowDown':
      event.preventDefault();
      navigateItems(event.key === 'ArrowUp' ? -1 : 1);
      break;
  }
};
```

### Focus Management
```typescript
// ✅ GOOD: Focus management in modals
export function Modal({ isOpen, onClose, children }: ModalProps) {
  const modalRef = useRef<HTMLDivElement>(null);
  
  useEffect(() => {
    if (isOpen && modalRef.current) {
      modalRef.current.focus();
    }
  }, [isOpen]);
  
  return (
    <div
      ref={modalRef}
      role="dialog"
      aria-modal="true"
      tabIndex={-1}
      className="focus:outline-none"
    >
      {children}
    </div>
  );
}
```

---

## 📝 Documentation Standards

### Component Documentation
```typescript
/**
 * JobCard component displays job information with action buttons.
 * 
 * @param job - The job object containing all job details
 * @param onApprove - Callback function called when job is approved
 * @param onReject - Callback function called when job is rejected
 * @param showActions - Whether to display action buttons (default: true)
 * @param compact - Whether to use compact layout (default: false)
 * 
 * @example
 * ```tsx
 * <JobCard
 *   job={jobData}
 *   onApprove={(jobId) => handleApprove(jobId)}
 *   onReject={(jobId, reason) => handleReject(jobId, reason)}
 *   showActions={true}
 * />
 * ```
 */
export function JobCard({ job, onApprove, onReject, showActions, compact }: JobCardProps) {
  // Implementation
}
```

### Code Comments
```typescript
// ✅ GOOD: Helpful comments explaining why, not what
// Debounce search input to prevent excessive API calls
const debouncedSearch = useMemo(
  () => debounce((query: string) => {
    searchJobs(query);
  }, 300),
  []
);

// Optimistic update: show change immediately, revert if fails
const handleStatusUpdate = async (jobId: string, newStatus: JobStatus) => {
  const originalStatus = job.status;
  updateJobStatus(jobId, newStatus); // Optimistic update
  
  try {
    await jobService.updateStatus(jobId, newStatus);
  } catch (error) {
    updateJobStatus(jobId, originalStatus); // Revert on failure
    showErrorMessage('Failed to update job status');
  }
};
```

---

This style guide serves as the definitive reference for all Dashboard v4 development work. Following these standards ensures consistency, maintainability, and accessibility across the entire project while enabling effective AI agent assistance. 