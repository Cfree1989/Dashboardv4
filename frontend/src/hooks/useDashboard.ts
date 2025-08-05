/**
 * Custom hook for managing dashboard data and state
 */

import { useState, useEffect, useCallback } from 'react';
import { apiClient, ApiClientError } from '@/lib/api-client';

interface DashboardStats {
  uploaded: number;
  pending: number;
  readyToPrint: number;
  printing: number;
  completed: number;
  total: number;
}

interface Job {
  id: string;
  student_name: string;
  student_email: string;
  display_name: string;
  status: string;
  created_at: string;
  printer: string;
  color: string;
  material: string;
  cost_usd?: number;
  needs_review?: boolean;
  age_hours?: number;
}

interface JobsResponse {
  jobs: Job[];
  pagination: {
    page: number;
    limit: number;
    total: number;
    pages: number;
    has_next: boolean;
    has_prev: boolean;
  };
  filters_applied: any;
}

export function useDashboard() {
  const [stats, setStats] = useState<DashboardStats>({
    uploaded: 0,
    pending: 0,
    readyToPrint: 0,
    printing: 0,
    completed: 0,
    total: 0,
  });
  
  const [jobs, setJobs] = useState<Job[]>([]);
  const [jobsLoading, setJobsLoading] = useState(true);
  const [statsLoading, setStatsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [pagination, setPagination] = useState({
    page: 1,
    limit: 50,
    total: 0,
    pages: 0,
    has_next: false,
    has_prev: false,
  });

  // Fetch dashboard statistics
  const fetchStats = useCallback(async () => {
    try {
      setStatsLoading(true);
      setError(null);
      const statsData = await apiClient.getDashboardStats();
      setStats(statsData);
    } catch (error) {
      console.error('Failed to fetch dashboard stats:', error);
      if (error instanceof ApiClientError) {
        setError(`Failed to load statistics: ${error.message}`);
      } else {
        setError('Failed to load statistics');
      }
    } finally {
      setStatsLoading(false);
    }
  }, []);

  // Fetch jobs list
  const fetchJobs = useCallback(async (params: {
    status?: string;
    search?: string;
    page?: number;
    limit?: number;
  } = {}) => {
    try {
      setJobsLoading(true);
      setError(null);
      
      const response = await apiClient.getJobs({
        page: 1,
        limit: 50,
        ...params,
      });
      
      setJobs(response.jobs);
      setPagination(response.pagination);
    } catch (error) {
      console.error('Failed to fetch jobs:', error);
      if (error instanceof ApiClientError) {
        setError(`Failed to load jobs: ${error.message}`);
      } else {
        setError('Failed to load jobs');
      }
    } finally {
      setJobsLoading(false);
    }
  }, []);

  // Refresh all data
  const refresh = useCallback(async () => {
    await Promise.all([
      fetchStats(),
      fetchJobs(),
    ]);
  }, [fetchStats, fetchJobs]);

  // Initial data load
  useEffect(() => {
    refresh();
  }, [refresh]);

  return {
    // Data
    stats,
    jobs,
    pagination,
    
    // Loading states
    statsLoading,
    jobsLoading,
    loading: statsLoading || jobsLoading,
    
    // Error state
    error,
    
    // Actions
    fetchJobs,
    fetchStats,
    refresh,
    
    // Computed values
    hasJobs: jobs.length > 0,
    needsReviewCount: jobs.filter(job => job.needs_review).length,
  };
}