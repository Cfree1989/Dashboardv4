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
    console.log('🔍 DEBUG: fetchStats called');
    try {
      setStatsLoading(true);
      setError(null);
      console.log('🔍 DEBUG: About to call apiClient.getDashboardStats()');
      const statsData = await apiClient.getDashboardStats();
      console.log('🔍 DEBUG: getDashboardStats response:', statsData);
      setStats(statsData);
    } catch (error) {
      console.error('❌ DEBUG: fetchStats error:', error);
      if (error instanceof ApiClientError) {
        setError(`Failed to load statistics: ${error.message}`);
      } else {
        setError('Failed to load statistics');
      }
    } finally {
      setStatsLoading(false);
      console.log('🔍 DEBUG: fetchStats completed');
    }
  }, []);

  // Fetch jobs list
  const fetchJobs = useCallback(async (params: {
    status?: string;
    search?: string;
    page?: number;
    limit?: number;
  } = {}) => {
    console.log('🔍 DEBUG: fetchJobs called with params:', params);
    try {
      setJobsLoading(true);
      setError(null);
      
      const requestParams = {
        page: 1,
        limit: 50,
        ...params,
      };
      console.log('🔍 DEBUG: About to call apiClient.getJobs() with:', requestParams);
      
      const response = await apiClient.getJobs(requestParams);
      console.log('🔍 DEBUG: getJobs response:', response);
      
      setJobs(response.jobs);
      setPagination(response.pagination);
    } catch (error) {
      console.error('❌ DEBUG: fetchJobs error:', error);
      if (error instanceof ApiClientError) {
        setError(`Failed to load jobs: ${error.message}`);
      } else {
        setError('Failed to load jobs');
      }
    } finally {
      setJobsLoading(false);
      console.log('🔍 DEBUG: fetchJobs completed');
    }
  }, []);

  // Refresh all data
  const refresh = useCallback(async () => {
    console.log('🔍 DEBUG: refresh() called - starting parallel fetch');
    await Promise.all([
      fetchStats(),
      fetchJobs(),
    ]);
    console.log('🔍 DEBUG: refresh() completed');
  }, [fetchStats, fetchJobs]);

  // Initial data load
  useEffect(() => {
    console.log('🔍 DEBUG: useDashboard useEffect triggered - calling refresh()');
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