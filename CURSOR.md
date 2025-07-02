# CURSOR.md - AI Agent Optimization Guide

This document contains Cursor-specific tips, bash aliases, red-flag patterns, and troubleshooting recipes for the Dashboard v4 project.

## 🤖 AI Agent Tips

### Project Context Understanding
- **Always check [`project-info.md`](./project-info.md)** before making changes to understand domain context
- **Reference the component library** in `v0/components/ui/` for existing UI patterns
- **Check existing types** in `v0/types/` before creating new interfaces
- **Follow the established patterns** in `v0/components/dashboard/` for consistency

### File Navigation Shortcuts
```bash
# Quick navigation to common directories
cd v0/                          # Main application
cd v0/components/dashboard/     # Dashboard components
cd v0/components/ui/            # Base UI components
cd docs/requirements/           # Requirements documentation
cd diagrams/ui-mockups/         # UI design references
```

### Common Development Tasks
1. **Adding a new component**: Check `v0/components/dashboard/` for patterns
2. **Updating types**: Modify files in `v0/types/` and update imports
3. **Styling changes**: Use Tailwind classes, check existing patterns first
4. **State management**: Use existing context in `dashboard-context.tsx`

## 🔧 Bash Aliases & Shortcuts

### Development Workflow
```bash
# Add these to your shell profile (.bashrc, .zshrc, etc.)

# Dashboard v4 specific aliases
alias dash='cd /path/to/Dashboardv4'
alias dashapp='cd /path/to/Dashboardv4/v0'
alias dashdocs='cd /path/to/Dashboardv4/docs'

# Next.js development
alias dev='pnpm dev'
alias build='pnpm build'
alias start='pnpm start'
alias lint='pnpm lint'
alias type-check='pnpm type-check'

# Testing
alias test='pnpm test'
alias test-watch='pnpm test --watch'
alias test-coverage='pnpm test --coverage'

# Git workflow
alias gst='git status'
alias gco='git checkout'
alias gcb='git checkout -b'
alias gad='git add .'
alias gcm='git commit -m'
alias gps='git push'
alias gpl='git pull'

# Component generation (if using generators)
alias new-component='plop component'
alias new-hook='plop hook'
```

### Quick Commands
```bash
# Project setup
pnpm install                    # Install dependencies
pnpm dev                       # Start development server
pnpm build                     # Build for production
pnpm lint                      # Run linting
pnpm type-check               # TypeScript checking

# File operations
find . -name "*.tsx" -type f   # Find all React components
grep -r "JobCard" v0/          # Search for component usage
```

## 🚨 Red-Flag Patterns

### Code Quality Issues
- **Missing TypeScript types**: All props and functions should have explicit types
- **Inconsistent naming**: Follow PascalCase for components, camelCase for functions
- **Direct DOM manipulation**: Use React patterns instead of direct DOM access
- **Inline styles**: Use Tailwind classes or CSS modules instead
- **Console.log statements**: Remove before production, use proper logging
- **Hardcoded values**: Use constants or configuration files
- **Missing error boundaries**: Wrap components that might fail
- **Unused imports**: Clean up imports regularly

### Architecture Anti-patterns
```typescript
// ❌ BAD: Direct state mutation
state.jobs.push(newJob);

// ✅ GOOD: Immutable state updates
setState(prev => [...prev, newJob]);

// ❌ BAD: Missing prop types
function JobCard({ job, onUpdate }) {

// ✅ GOOD: Explicit prop types
interface JobCardProps {
  job: Job;
  onUpdate: (job: Job) => void;
}
function JobCard({ job, onUpdate }: JobCardProps) {

// ❌ BAD: Side effects in render
function Component() {
  updateDatabase(); // Side effect in render
  return <div>...</div>;
}

// ✅ GOOD: Side effects in useEffect
function Component() {
  useEffect(() => {
    updateDatabase();
  }, []);
  return <div>...</div>;
}
```

### File Organization Issues
- **Components in wrong directories**: Dashboard components go in `components/dashboard/`
- **Missing barrel exports**: Use `index.ts` files for clean imports
- **Circular dependencies**: Avoid components importing each other directly
- **Deep nesting**: Keep component hierarchy shallow when possible

## 🔧 Troubleshooting Recipes

### Common Issues & Solutions

#### 1. TypeScript Errors
```bash
# Problem: Type errors during development
# Solution: Run type checking
pnpm type-check

# Problem: Missing type definitions
# Solution: Check if types exist in v0/types/
ls v0/types/

# Problem: Import path errors
# Solution: Use relative imports or check tsconfig paths
```

#### 2. Component Rendering Issues
```typescript
// Problem: Component not updating
// Check: Are you mutating state directly?
// Solution: Use immutable updates

// Problem: Props not passing correctly
// Check: TypeScript prop interfaces
// Solution: Verify prop names and types match

// Problem: Styling not applied
// Check: Tailwind classes are correct
// Solution: Verify class names in Tailwind docs
```

#### 3. State Management Issues
```typescript
// Problem: State not persisting across components
// Solution: Use dashboard context
import { useDashboard } from '../dashboard-context';

// Problem: Stale closures in useEffect
// Solution: Add dependencies to dependency array
useEffect(() => {
  // function using state
}, [stateVariable]); // Include all dependencies
```

#### 4. Build & Development Issues
```bash
# Problem: Development server won't start
cd v0 && pnpm install && pnpm dev

# Problem: Build failures
pnpm build
# Check console for specific errors

# Problem: Linting errors
pnpm lint --fix
# Auto-fix common issues

# Problem: Module not found errors
# Check import paths and file names
# Ensure components are exported properly
```

#### 5. Performance Issues
```typescript
// Problem: Slow re-renders
// Solution: Memoize expensive components
const MemoizedComponent = React.memo(ExpensiveComponent);

// Problem: Unnecessary re-renders
// Solution: Optimize context providers
const contextValue = useMemo(() => ({
  data,
  actions
}), [data]);

// Problem: Large bundle size
// Solution: Check for unused imports and components
```

### Debugging Workflow
1. **Check Console**: Look for errors and warnings
2. **Verify Types**: Run `pnpm type-check`
3. **Check Imports**: Ensure all imports are correct
4. **Test Components**: Isolate problematic components
5. **Review Context**: Check state management flow
6. **Validate Props**: Ensure props match interface definitions

## 📚 Useful Resources

### Documentation Quick Links
- [Next.js App Router](https://nextjs.org/docs/app)
- [React TypeScript](https://react-typescript-cheatsheet.netlify.app/)
- [Tailwind CSS](https://tailwindcss.com/docs)
- [shadcn/ui Components](https://ui.shadcn.com/docs)

### Development Tools
- **VS Code Extensions**: 
  - TypeScript Importer
  - ES7+ React/Redux/React-Native snippets
  - Tailwind CSS IntelliSense
  - Auto Rename Tag
- **Browser DevTools**: React Developer Tools, TypeScript debugging

### Code Quality Tools
```bash
# ESLint configuration check
pnpm lint --print-config .

# Prettier formatting check
pnpm prettier --check .

# TypeScript configuration
cat v0/tsconfig.json
```

## 🎯 AI Agent Best Practices

### Before Making Changes
1. **Read project-info.md** for context
2. **Check existing patterns** in similar components
3. **Verify type definitions** are available
4. **Review component props** and interfaces

### During Development
1. **Follow naming conventions** consistently
2. **Add TypeScript types** for all new code
3. **Use existing UI components** when possible
4. **Test changes** in development server

### After Changes
1. **Run type checking** (`pnpm type-check`)
2. **Check linting** (`pnpm lint`)
3. **Test functionality** manually
4. **Update documentation** if needed

### Communication Patterns
- **Be specific** about file paths and component names
- **Reference existing patterns** when explaining changes
- **Include type definitions** in code examples
- **Mention testing** requirements for new features

This guide should help AI agents work more effectively with the Dashboard v4 codebase by providing context, patterns, and troubleshooting approaches. 