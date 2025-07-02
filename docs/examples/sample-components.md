# Sample Components - Dashboard v4

This document provides comprehensive examples of React components following Dashboard v4 patterns and conventions. These examples serve as templates for new development and reference for AI agents.

## 📋 Component Examples

### Job Card Component

```typescript
// components/dashboard/job-card.tsx
import React from 'react';
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { CalendarIcon, ClockIcon, UserIcon } from 'lucide-react';
import { cn } from '@/lib/utils';
import type { Job, JobStatus, Priority } from '@/types/job';

interface JobCardProps {
  job: Job;
  onApprove?: (jobId: string) => void;
  onReject?: (jobId: string, reason: string) => void;
  showActions?: boolean;
  compact?: boolean;
  className?: string;
}

export function JobCard({ 
  job, 
  onApprove, 
  onReject, 
  showActions = true,
  compact = false,
  className 
}: JobCardProps) {
  const getStatusColor = (status: JobStatus): string => {
    switch (status) {
      case 'pending': return 'bg-amber-100 text-amber-800 border-amber-200';
      case 'approved': return 'bg-green-100 text-green-800 border-green-200';
      case 'rejected': return 'bg-red-100 text-red-800 border-red-200';
      case 'completed': return 'bg-gray-100 text-gray-800 border-gray-200';
      default: return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getPriorityColor = (priority: Priority): string => {
    switch (priority) {
      case 'urgent': return 'text-red-600';
      case 'high': return 'text-orange-600';
      case 'medium': return 'text-yellow-600';
      case 'low': return 'text-green-600';
      default: return 'text-gray-600';
    }
  };

  return (
    <Card className={cn(
      "transition-all duration-200 hover:shadow-md",
      compact ? "p-3" : "p-4",
      className
    )}>
      <CardHeader className={cn("pb-2", compact && "pb-1")}>
        <div className="flex items-start justify-between gap-3">
          <CardTitle className={cn(
            compact ? "text-base" : "text-lg",
            "line-clamp-2 font-medium"
          )}>
            {job.title}
          </CardTitle>
          <Badge 
            variant="secondary"
            className={cn("shrink-0", getStatusColor(job.status))}
          >
            {job.status}
          </Badge>
        </div>
      </CardHeader>
      
      <CardContent className={cn("space-y-2", compact && "space-y-1")}>
        {job.description && (
          <p className="text-sm text-gray-600 line-clamp-2">
            {job.description}
          </p>
        )}
        
        <div className="flex items-center gap-4 text-xs text-gray-500">
          <div className="flex items-center gap-1">
            <ClockIcon className="w-3 h-3" />
            <span className={getPriorityColor(job.priority)}>
              {job.priority}
            </span>
          </div>
          
          <div className="flex items-center gap-1">
            <CalendarIcon className="w-3 h-3" />
            <span>{new Date(job.createdAt).toLocaleDateString()}</span>
          </div>
          
          {job.assignedTo && (
            <div className="flex items-center gap-1">
              <UserIcon className="w-3 h-3" />
              <span>{job.assignedTo}</span>
            </div>
          )}
        </div>
      </CardContent>
      
      {showActions && job.status === 'pending' && (
        <CardFooter className={cn("pt-2 gap-2", compact && "pt-1")}>
          <Button
            size="sm"
            variant="outline"
            onClick={() => onReject?.(job.id, '')}
            className="flex-1"
          >
            Reject
          </Button>
          <Button
            size="sm"
            onClick={() => onApprove?.(job.id)}
            className="flex-1"
          >
            Approve
          </Button>
        </CardFooter>
      )}
    </Card>
  );
}

// Usage Example
export function JobCardExample() {
  const sampleJob: Job = {
    id: 'job-001',
    title: 'Review Marketing Campaign Assets',
    description: 'Review and approve the Q1 marketing campaign materials including graphics, copy, and video content.',
    status: 'pending',
    priority: 'high',
    createdAt: new Date().toISOString(),
    assignedTo: 'John Doe'
  };

  const handleApprove = (jobId: string) => {
    console.log('Approving job:', jobId);
  };

  const handleReject = (jobId: string, reason: string) => {
    console.log('Rejecting job:', jobId, 'Reason:', reason);
  };

  return (
    <div className="max-w-sm">
      <JobCard
        job={sampleJob}
        onApprove={handleApprove}
        onReject={handleReject}
      />
    </div>
  );
}
```

### Status Filter Tabs Component

```typescript
// components/dashboard/status-tabs.tsx
import React from 'react';
import { Tabs, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import type { JobStatus } from '@/types/job';

interface StatusTabsProps {
  activeStatus: JobStatus | 'all';
  onStatusChange: (status: JobStatus | 'all') => void;
  jobCounts: Record<JobStatus | 'all', number>;
  className?: string;
}

export function StatusTabs({ 
  activeStatus, 
  onStatusChange, 
  jobCounts,
  className 
}: StatusTabsProps) {
  const statusConfig = [
    { key: 'all' as const, label: 'All Jobs', color: 'bg-gray-100 text-gray-800' },
    { key: 'pending' as const, label: 'Pending', color: 'bg-amber-100 text-amber-800' },
    { key: 'approved' as const, label: 'Approved', color: 'bg-green-100 text-green-800' },
    { key: 'rejected' as const, label: 'Rejected', color: 'bg-red-100 text-red-800' },
    { key: 'completed' as const, label: 'Completed', color: 'bg-gray-100 text-gray-800' }
  ];

  return (
    <Tabs 
      value={activeStatus} 
      onValueChange={(value) => onStatusChange(value as JobStatus | 'all')}
      className={className}
    >
      <TabsList className="grid w-full grid-cols-5 lg:w-auto lg:grid-cols-none lg:inline-flex">
        {statusConfig.map(({ key, label, color }) => (
          <TabsTrigger
            key={key}
            value={key}
            className="flex items-center gap-2 px-3 py-2"
          >
            <span className="hidden sm:inline">{label}</span>
            <span className="sm:hidden">{label.split(' ')[0]}</span>
            <Badge 
              variant="secondary"
              className={`${color} text-xs px-1.5 py-0.5 min-w-[1.5rem] justify-center`}
            >
              {jobCounts[key] || 0}
            </Badge>
          </TabsTrigger>
        ))}
      </TabsList>
    </Tabs>
  );
}

// Usage Example
export function StatusTabsExample() {
  const [activeStatus, setActiveStatus] = React.useState<JobStatus | 'all'>('all');
  
  const jobCounts = {
    all: 42,
    pending: 12,
    approved: 18,
    rejected: 5,
    completed: 7
  };

  return (
    <StatusTabs
      activeStatus={activeStatus}
      onStatusChange={setActiveStatus}
      jobCounts={jobCounts}
    />
  );
}
```

### Job Action Modal Component

```typescript
// components/dashboard/job-action-modal.tsx
import React, { useState } from 'react';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { AlertCircle, CheckCircle2 } from 'lucide-react';
import type { Job } from '@/types/job';

interface JobActionModalProps {
  job: Job | null;
  isOpen: boolean;
  onClose: () => void;
  onConfirm: (data: { jobId: string; notes?: string; reason?: string }) => void;
  action: 'approve' | 'reject';
  loading?: boolean;
}

export function JobActionModal({
  job,
  isOpen,
  onClose,
  onConfirm,
  action,
  loading = false
}: JobActionModalProps) {
  const [notes, setNotes] = useState('');
  const [reason, setReason] = useState('');
  
  const isApproval = action === 'approve';
  const isReasonRequired = !isApproval && reason.trim().length < 10;

  const handleConfirm = () => {
    if (!job) return;
    
    onConfirm({
      jobId: job.id,
      notes: isApproval ? notes : undefined,
      reason: !isApproval ? reason : undefined
    });
    
    // Reset form
    setNotes('');
    setReason('');
  };

  const handleClose = () => {
    setNotes('');
    setReason('');
    onClose();
  };

  if (!job) return null;

  return (
    <Dialog open={isOpen} onOpenChange={handleClose}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            {isApproval ? (
              <CheckCircle2 className="w-5 h-5 text-green-600" />
            ) : (
              <AlertCircle className="w-5 h-5 text-red-600" />
            )}
            {isApproval ? 'Approve Job' : 'Reject Job'}
          </DialogTitle>
          <DialogDescription>
            {isApproval 
              ? 'Confirm approval to proceed with this job.'
              : 'Please provide a reason for rejecting this job.'
            }
          </DialogDescription>
        </DialogHeader>
        
        <div className="py-4 space-y-4">
          {/* Job Information */}
          <div className="p-3 bg-gray-50 rounded-lg space-y-2">
            <div className="flex items-center justify-between">
              <h4 className="font-medium text-sm">Job Details</h4>
              <Badge variant={job.status === 'pending' ? 'default' : 'secondary'}>
                {job.status}
              </Badge>
            </div>
            
            <div>
              <p className="font-medium">{job.title}</p>
              {job.description && (
                <p className="text-sm text-gray-600 mt-1">{job.description}</p>
              )}
            </div>
            
            <div className="flex items-center gap-4 text-xs text-gray-500">
              <span>Priority: {job.priority}</span>
              <span>Created: {new Date(job.createdAt).toLocaleDateString()}</span>
            </div>
          </div>
          
          {/* Input Field */}
          <div className="space-y-2">
            <Label htmlFor={isApproval ? 'notes' : 'reason'}>
              {isApproval ? 'Notes (Optional)' : 'Rejection Reason'}
              {!isAprroval && <span className="text-red-500 ml-1">*</span>}
            </Label>
            
            <Textarea
              id={isApproval ? 'notes' : 'reason'}
              placeholder={
                isApproval 
                  ? 'Add any notes about this approval...'
                  : 'Please explain why this job is being rejected...'
              }
              value={isApproval ? notes : reason}
              onChange={(e) => {
                if (isApproval) {
                  setNotes(e.target.value);
                } else {
                  setReason(e.target.value);
                }
              }}
              className="min-h-[80px]"
              maxLength={500}
            />
            
            <div className="flex justify-between text-xs text-gray-500">
              {!isApproval && isReasonRequired && (
                <span className="text-red-500">
                  Reason must be at least 10 characters
                </span>
              )}
              <span className="ml-auto">
                {(isApproval ? notes : reason).length}/500
              </span>
            </div>
          </div>
        </div>
        
        <DialogFooter>
          <Button variant="outline" onClick={handleClose} disabled={loading}>
            Cancel
          </Button>
          <Button
            onClick={handleConfirm}
            disabled={loading || isReasonRequired}
            className={isApproval ? '' : 'bg-red-600 hover:bg-red-700'}
          >
            {loading ? 'Processing...' : (isApproval ? 'Approve' : 'Reject')}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}

// Usage Example
export function JobActionModalExample() {
  const [modalOpen, setModalOpen] = useState(false);
  const [action, setAction] = useState<'approve' | 'reject'>('approve');
  
  const sampleJob: Job = {
    id: 'job-001',
    title: 'Review Marketing Campaign',
    description: 'Review Q1 marketing materials',
    status: 'pending',
    priority: 'high',
    createdAt: new Date().toISOString()
  };

  const handleConfirm = (data: { jobId: string; notes?: string; reason?: string }) => {
    console.log('Action confirmed:', data);
    setModalOpen(false);
  };

  return (
    <div className="space-x-2">
      <Button onClick={() => { setAction('approve'); setModalOpen(true); }}>
        Approve Job
      </Button>
      <Button 
        variant="destructive" 
        onClick={() => { setAction('reject'); setModalOpen(true); }}
      >
        Reject Job
      </Button>
      
      <JobActionModal
        job={sampleJob}
        isOpen={modalOpen}
        onClose={() => setModalOpen(false)}
        onConfirm={handleConfirm}
        action={action}
      />
    </div>
  );
}
```

### Sound Toggle Component

```typescript
// components/dashboard/sound-toggle.tsx
import React from 'react';
import { Button } from '@/components/ui/button';
import { Volume2, VolumeX } from 'lucide-react';
import { cn } from '@/lib/utils';

interface SoundToggleProps {
  enabled: boolean;
  onToggle: (enabled: boolean) => void;
  className?: string;
}

export function SoundToggle({ enabled, onToggle, className }: SoundToggleProps) {
  return (
    <Button
      variant="ghost"
      size="sm"
      onClick={() => onToggle(!enabled)}
      className={cn(
        "h-8 w-8 p-0",
        enabled ? "text-blue-600 hover:text-blue-700" : "text-gray-400 hover:text-gray-500",
        className
      )}
      aria-label={enabled ? "Disable sound notifications" : "Enable sound notifications"}
    >
      {enabled ? (
        <Volume2 className="h-4 w-4" />
      ) : (
        <VolumeX className="h-4 w-4" />
      )}
    </Button>
  );
}

// Usage Example
export function SoundToggleExample() {
  const [soundEnabled, setSoundEnabled] = React.useState(true);

  return (
    <div className="flex items-center gap-2">
      <span className="text-sm">Sound notifications:</span>
      <SoundToggle
        enabled={soundEnabled}
        onToggle={setSoundEnabled}
      />
      <span className="text-xs text-gray-500">
        {soundEnabled ? 'On' : 'Off'}
      </span>
    </div>
  );
}
```

### Custom Hook Examples

```typescript
// hooks/use-jobs.ts
import { useState, useEffect, useCallback } from 'react';
import type { Job, JobStatus } from '@/types/job';

interface UseJobsOptions {
  status?: JobStatus | 'all';
  autoRefresh?: boolean;
  refreshInterval?: number;
}

interface UseJobsReturn {
  jobs: Job[];
  loading: boolean;
  error: string | null;
  refetch: () => Promise<void>;
  approveJob: (jobId: string, notes?: string) => Promise<void>;
  rejectJob: (jobId: string, reason: string) => Promise<void>;
}

export function useJobs(options: UseJobsOptions = {}): UseJobsReturn {
  const { status = 'all', autoRefresh = true, refreshInterval = 30000 } = options;
  
  const [jobs, setJobs] = useState<Job[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchJobs = useCallback(async () => {
    try {
      setError(null);
      const url = status === 'all' ? '/api/jobs' : `/api/jobs?status=${status}`;
      const response = await fetch(url);
      
      if (!response.ok) {
        throw new Error(`Failed to fetch jobs: ${response.statusText}`);
      }
      
      const data = await response.json();
      setJobs(data.jobs || []);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error occurred');
    } finally {
      setLoading(false);
    }
  }, [status]);

  const approveJob = useCallback(async (jobId: string, notes?: string) => {
    try {
      const response = await fetch(`/api/jobs/${jobId}/approve`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ notes })
      });

      if (!response.ok) {
        throw new Error('Failed to approve job');
      }

      // Optimistic update
      setJobs(prev => prev.map(job => 
        job.id === jobId ? { ...job, status: 'approved' as JobStatus } : job
      ));
      
      // Refetch to ensure consistency
      await fetchJobs();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to approve job');
      throw err;
    }
  }, [fetchJobs]);

  const rejectJob = useCallback(async (jobId: string, reason: string) => {
    try {
      const response = await fetch(`/api/jobs/${jobId}/reject`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ reason })
      });

      if (!response.ok) {
        throw new Error('Failed to reject job');
      }

      // Optimistic update
      setJobs(prev => prev.map(job => 
        job.id === jobId ? { ...job, status: 'rejected' as JobStatus } : job
      ));
      
      // Refetch to ensure consistency
      await fetchJobs();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to reject job');
      throw err;
    }
  }, [fetchJobs]);

  // Initial fetch
  useEffect(() => {
    fetchJobs();
  }, [fetchJobs]);

  // Auto-refresh
  useEffect(() => {
    if (!autoRefresh) return;

    const interval = setInterval(fetchJobs, refreshInterval);
    return () => clearInterval(interval);
  }, [fetchJobs, autoRefresh, refreshInterval]);

  return {
    jobs,
    loading,
    error,
    refetch: fetchJobs,
    approveJob,
    rejectJob
  };
}

// Usage Example
export function useJobsExample() {
  const { jobs, loading, error, approveJob, rejectJob } = useJobs({
    status: 'pending',
    autoRefresh: true
  });

  const handleApprove = async (jobId: string) => {
    try {
      await approveJob(jobId, 'Approved via dashboard');
      console.log('Job approved successfully');
    } catch (error) {
      console.error('Failed to approve job:', error);
    }
  };

  return { jobs, loading, error, handleApprove };
}
```

### Dashboard Layout Component

```typescript
// components/dashboard/dashboard-layout.tsx
import React from 'react';
import { cn } from '@/lib/utils';

interface DashboardLayoutProps {
  header?: React.ReactNode;
  sidebar?: React.ReactNode;
  children: React.ReactNode;
  className?: string;
}

export function DashboardLayout({ 
  header, 
  sidebar, 
  children, 
  className 
}: DashboardLayoutProps) {
  return (
    <div className={cn("min-h-screen bg-gray-50", className)}>
      {/* Header */}
      {header && (
        <header className="sticky top-0 z-50 bg-white border-b border-gray-200">
          <div className="px-4 sm:px-6 lg:px-8">
            {header}
          </div>
        </header>
      )}
      
      <div className="flex h-full">
        {/* Sidebar */}
        {sidebar && (
          <aside className="hidden lg:block w-64 bg-white border-r border-gray-200">
            <div className="h-full p-4">
              {sidebar}
            </div>
          </aside>
        )}
        
        {/* Main Content */}
        <main className="flex-1 overflow-auto">
          <div className="p-4 sm:p-6 lg:p-8">
            {children}
          </div>
        </main>
      </div>
    </div>
  );
}

// Usage Example
export function DashboardLayoutExample() {
  return (
    <DashboardLayout
      header={
        <div className="flex items-center justify-between h-16">
          <h1 className="text-xl font-semibold">Dashboard v4</h1>
          <div className="flex items-center gap-4">
            <SoundToggle enabled={true} onToggle={() => {}} />
          </div>
        </div>
      }
      sidebar={
        <nav className="space-y-2">
          <a href="#" className="block px-3 py-2 rounded-md text-sm font-medium bg-blue-100 text-blue-700">
            Jobs
          </a>
          <a href="#" className="block px-3 py-2 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-100">
            Analytics
          </a>
          <a href="#" className="block px-3 py-2 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-100">
            Settings
          </a>
        </nav>
      }
    >
      <div className="space-y-6">
        <StatusTabsExample />
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <JobCardExample />
          <JobCardExample />
          <JobCardExample />
        </div>
      </div>
    </DashboardLayout>
  );
}
```

## 📝 Pattern Guidelines

### Component Naming
- Use PascalCase for component names
- Use clear, descriptive names that indicate component purpose
- Prefix with domain context when needed (e.g., `JobCard`, `DashboardLayout`)

### Props Interface
- Always define explicit TypeScript interfaces for props
- Use optional props with default values where appropriate
- Include `className` prop for styling flexibility
- Add JSDoc comments for complex props

### State Management
- Use local state for component-specific state
- Use custom hooks to encapsulate reusable logic
- Implement optimistic updates for better UX
- Handle loading and error states consistently

### Accessibility
- Include proper ARIA labels and roles
- Support keyboard navigation
- Ensure sufficient color contrast
- Use semantic HTML elements

### Styling
- Use Tailwind CSS classes following the established order
- Implement responsive design with mobile-first approach
- Use consistent spacing from the design system
- Support dark mode where applicable (future enhancement)

These component examples demonstrate the patterns and conventions used throughout Dashboard v4, providing clear templates for new development and consistent reference for AI agents. 