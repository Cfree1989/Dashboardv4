'use client'

import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { ProtectedRoute, useAuthStatus } from '@/lib/auth-middleware';
import { useAuth } from '@/lib/auth-context';
import { useDashboard } from '@/hooks/useDashboard';
import { JobCard } from '@/components/dashboard/job-card';

function DashboardContent() {
  const { logout } = useAuth();
  const { workstationId, staffName } = useAuthStatus();
  const { 
    stats, 
    jobs, 
    loading, 
    error, 
    refresh, 
    hasJobs,
    needsReviewCount 
  } = useDashboard();

  const handleLogout = async () => {
    try {
      await logout();
    } catch (error) {
      console.error('Logout failed:', error);
    }
  };

  const formatJobForCard = (job: any) => ({
    id: job.id,
    studentName: job.student_name,
    projectTitle: job.display_name,
    status: job.status as 'UPLOADED' | 'PENDING' | 'READYTOPRINT' | 'PRINTING' | 'COMPLETED' | 'PAIDPICKEDUP' | 'REJECTED' | 'ARCHIVED',
    fileName: job.display_name,
    submittedAt: new Date(job.created_at).toLocaleDateString(),
    estimatedCost: job.cost_usd ? parseFloat(job.cost_usd) : undefined,
  });
  return (
    <div className="container mx-auto p-6">
      <div className="mb-8 flex justify-between items-start">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">3D Print Dashboard</h1>
          <p className="text-muted-foreground">
            Manage 3D print jobs and workflow status
          </p>
          {workstationId && staffName && (
            <p className="text-sm text-muted-foreground mt-2">
              Logged in as <strong>{staffName}</strong> on <strong>{workstationId}</strong>
            </p>
          )}
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={refresh} disabled={loading}>
            {loading ? 'Refreshing...' : 'Refresh'}
          </Button>
          <Button variant="outline" onClick={handleLogout}>
            Logout
          </Button>
        </div>
      </div>

      {error && (
        <Alert className="mb-6 border-red-200 bg-red-50">
          <AlertDescription className="text-red-800">
            {error}
          </AlertDescription>
        </Alert>
      )}

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">
              New Uploads
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {loading ? '...' : stats.uploaded}
            </div>
            <p className="text-xs text-muted-foreground">
              Awaiting review
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">
              Pending Approval
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {loading ? '...' : stats.pending}
            </div>
            <p className="text-xs text-muted-foreground">
              Awaiting student confirmation
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">
              Ready to Print
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {loading ? '...' : stats.readyToPrint}
            </div>
            <p className="text-xs text-muted-foreground">
              Confirmed by students
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">
              Currently Printing
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {loading ? '...' : stats.printing}
            </div>
            <p className="text-xs text-muted-foreground">
              In progress
            </p>
          </CardContent>
        </Card>
      </div>

      <Card className="mt-6">
        <CardHeader>
          <CardTitle>Recent Jobs</CardTitle>
          <CardDescription>
            {loading ? 'Loading jobs...' : `${jobs.length} jobs in the system`}
          </CardDescription>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="text-center py-8 text-muted-foreground">
              Loading jobs...
            </div>
          ) : !hasJobs ? (
            <div className="text-center py-8 text-muted-foreground">
              No jobs currently in the system
            </div>
          ) : (
            <div className="space-y-4">
              {jobs.slice(0, 10).map((job) => (
                <JobCard
                  key={job.id}
                  {...formatJobForCard(job)}
                  onRefresh={refresh}
                />
              ))}
              {jobs.length > 10 && (
                <div className="text-center pt-4">
                  <p className="text-sm text-muted-foreground">
                    Showing 10 of {jobs.length} jobs
                  </p>
                </div>
              )}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

export default function DashboardPage() {
  return (
    <ProtectedRoute
      requireAuth={true}
      requireStaffSelection={true}
    >
      <DashboardContent />
    </ProtectedRoute>
  );
}