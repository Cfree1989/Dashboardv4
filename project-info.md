# Dashboard v4 - Project Information

This document serves as the "minimal brain" for the Dashboard v4 project, containing essential context, goals, and conventions that AI coding agents need to understand the project effectively.

## 🎯 Project Goals

### Primary Objectives
- **Create a modern, responsive dashboard** for job management and tracking
- **Optimize for AI coding agent effectiveness** through clear structure and documentation
- **Implement reusable component architecture** using React and TypeScript
- **Provide real-time job status updates** with sound notifications and visual indicators
- **Enable efficient development workflow** with automated testing and CI/CD

### Success Metrics
- **Performance**: Sub-2s initial load times, smooth animations
- **Accessibility**: WCAG 2.1 AA compliance
- **Code Quality**: 90%+ test coverage, consistent TypeScript usage
- **Developer Experience**: Clear documentation, easy onboarding
- **AI Agent Compatibility**: Structured for easy AI navigation and understanding

## 🏢 Domain Context

### Business Domain: Job Management Dashboard

**Core Entities:**
- **Job**: A work item with status, priority, and metadata
- **Status**: Current state of a job (pending, approved, rejected, completed)
- **Priority**: Urgency level (low, medium, high, urgent)
- **User**: Person interacting with the dashboard
- **Notification**: System alerts and updates

**Key Workflows:**
1. **Job Submission**: Create new jobs with required details
2. **Status Management**: Update job status through approval/rejection flows
3. **Monitoring**: Real-time tracking of job progress and updates
4. **Notification**: Audio/visual alerts for status changes

## 📖 Domain Glossary

### Job Management Terms
| Term | Definition | Context |
|------|------------|---------|
| **Job** | A unit of work with defined requirements and status | Core entity in the system |
| **Status** | Current state of a job (pending, approved, rejected, etc.) | Drives workflow logic |
| **Priority** | Importance level affecting job ordering and visibility | Business rule enforcement |
| **Queue** | Collection of jobs organized by status or priority | System organization |
| **Dashboard** | Main interface showing job overview and metrics | User interface |
| **Modal** | Overlay dialog for job actions (approve/reject) | UI interaction pattern |
| **Card** | Visual representation of a job with key details | Component pattern |
| **Toast** | Temporary notification message | User feedback mechanism |
| **Sound Toggle** | User preference for audio notifications | Feature control |

### Technical Terms
| Term | Definition | Context |
|------|------------|---------|
| **Component** | Reusable React component with defined props | Architecture pattern |
| **Hook** | Custom React hook for shared logic | Code organization |
| **Type** | TypeScript type definition for data structures | Type safety |
| **Context** | React Context for state management | State sharing |
| **Provider** | Component that supplies context values | State management |
| **Shadcn/ui** | UI component library used throughout the project | Design system |
| **Tailwind** | Utility-first CSS framework | Styling approach |

## 🛠 Coding Conventions

### File Naming
- **Components**: PascalCase (e.g., `JobCard.tsx`, `StatusTabs.tsx`)
- **Hooks**: camelCase starting with "use" (e.g., `useJobData.ts`)
- **Types**: PascalCase in `types/` directory (e.g., `Job.ts`)
- **Utilities**: camelCase (e.g., `formatDate.ts`)
- **Pages**: kebab-case (e.g., `dashboard/page.tsx`)

### Directory Structure
```
v0/
├── app/                        # Next.js 13+ app directory
├── components/                 # Reusable components
│   ├── dashboard/             # Dashboard-specific components
│   ├── ui/                    # Base UI components (shadcn/ui)
│   └── theme-provider.tsx     # Theme management
├── hooks/                     # Custom React hooks
├── lib/                       # Utility functions and configurations
├── types/                     # TypeScript type definitions
└── public/                    # Static assets
```

### Code Style Guidelines
- **TypeScript**: Strict mode enabled, explicit types preferred
- **React**: Functional components with hooks, no class components
- **Props**: Interface definitions for all component props
- **State**: Use React hooks (useState, useEffect, useContext)
- **Styling**: Tailwind CSS classes, component-scoped styles
- **Comments**: JSDoc for functions, inline comments for complex logic

### Component Patterns
```typescript
// Standard component structure
interface ComponentProps {
  // Props definition
}

export function ComponentName({ prop1, prop2 }: ComponentProps) {
  // Hooks at the top
  const [state, setState] = useState();
  
  // Event handlers
  const handleAction = () => {
    // Logic here
  };
  
  // Render
  return (
    <div className="tailwind-classes">
      {/* JSX content */}
    </div>
  );
}
```

### State Management
- **Local State**: `useState` for component-specific state
- **Global State**: React Context for shared dashboard state
- **Server State**: React Query or SWR for API data (when implemented)
- **Form State**: React Hook Form for complex forms

## 🔧 Repository Etiquette

### Branch Management
- **Main Branch**: `master` - production-ready code
- **Feature Branches**: `feature/description` - new features
- **Bug Fixes**: `fix/description` - bug fixes
- **Documentation**: `docs/description` - documentation updates

### Commit Messages
- **Format**: `type(scope): description`
- **Types**: feat, fix, docs, style, refactor, test, chore
- **Examples**: 
  - `feat(dashboard): add job approval modal`
  - `fix(components): resolve status tab navigation`
  - `docs(readme): update setup instructions`

### Pull Request Guidelines
- **Title**: Clear, descriptive summary
- **Description**: Context, changes, and testing notes
- **Review**: At least one approval required
- **Testing**: Include test results or screenshots

### Code Quality Standards
- **Linting**: ESLint rules enforced
- **Formatting**: Prettier for consistent style
- **Type Checking**: TypeScript strict mode
- **Testing**: Jest + React Testing Library
- **Coverage**: Aim for 80%+ test coverage

## 🎨 Design System

### Color Scheme
- **Primary**: Dashboard blue tones
- **Secondary**: Accent colors for status states
- **Neutral**: Grays for text and backgrounds
- **Semantic**: Green (success), Red (error), Yellow (warning)

### Typography
- **Headings**: Font weights 600-700
- **Body Text**: Font weight 400
- **Hierarchy**: Clear size differentiation

### Spacing
- **Grid**: 4px base unit
- **Components**: Consistent padding and margins
- **Layout**: Responsive spacing for different screen sizes

## 🔍 AI Agent Optimization Notes

### File Organization
- **Predictable Structure**: Consistent naming and folder organization
- **Clear Dependencies**: Import paths follow established patterns
- **Documentation**: Every major component and function documented

### Context Preservation
- **Type Definitions**: Comprehensive TypeScript types
- **Component Props**: Well-defined interfaces
- **Business Logic**: Documented in domain glossary
- **State Flow**: Clear state management patterns

### Common Patterns
- **Data Fetching**: Consistent async patterns
- **Error Handling**: Standardized error boundaries and messaging
- **Loading States**: Consistent loading indicators
- **Form Handling**: Standardized form validation and submission

This document should be referenced frequently to maintain consistency and provide context for AI-assisted development. 