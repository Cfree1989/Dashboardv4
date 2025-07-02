// Integration test for job approval workflow
import { render, screen, waitFor } from '../../config/test-utils';
import { setupServer } from 'msw/node';
import { rest } from 'msw';
import userEvent from '@testing-library/user-event';
import { Dashboard } from '../../../Project Information/v0/components/dashboard/dashboard';
import sampleJobs from '../../fixtures/jobs.json';

// Setup MSW server for API mocking
const server = setupServer(
  // Mock GET /api/jobs
  rest.get('/api/jobs', (req, res, ctx) => {
    const status = req.url.searchParams.get('status');
    
    if (status && status !== 'all') {
      const filteredJobs = sampleJobs.sampleJobs.filter(job => job.status === status);
      return res(ctx.json({ jobs: filteredJobs, total: filteredJobs.length }));
    }
    
    return res(ctx.json({ 
      jobs: sampleJobs.sampleJobs, 
      total: sampleJobs.sampleJobs.length 
    }));
  }),

  // Mock POST /api/jobs/:id/approve
  rest.post('/api/jobs/:id/approve', (req, res, ctx) => {
    const { id } = req.params;
    return res(ctx.json({ 
      success: true, 
      message: 'Job approved successfully',
      jobId: id 
    }));
  }),

  // Mock POST /api/jobs/:id/reject
  rest.post('/api/jobs/:id/reject', (req, res, ctx) => {
    const { id } = req.params;
    return res(ctx.json({ 
      success: true, 
      message: 'Job rejected successfully',
      jobId: id 
    }));
  })
);

// Setup and teardown MSW
beforeAll(() => server.listen({ onUnhandledRequest: 'error' }));
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

describe('Job Approval Workflow Integration', () => {
  beforeEach(() => {
    // Clear any stored state
    localStorage.clear();
  });

  describe('Complete Approval Flow', () => {
    it('successfully approves a job from start to finish', async () => {
      const user = userEvent.setup();
      render(<Dashboard />);

      // Wait for initial job load
      await waitFor(() => {
        expect(screen.getByText('Review Marketing Campaign Assets')).toBeInTheDocument();
      });

      // Verify pending jobs are visible
      expect(screen.getByText('pending')).toBeInTheDocument();

      // Click approve button on first pending job
      const approveButton = screen.getByRole('button', { name: /approve/i });
      await user.click(approveButton);

      // Verify approval modal opens
      await waitFor(() => {
        expect(screen.getByRole('dialog')).toBeInTheDocument();
        expect(screen.getByText(/approve job/i)).toBeInTheDocument();
      });

      // Add optional approval notes
      const notesField = screen.getByLabelText(/notes/i);
      await user.type(notesField, 'Approved after review - looks good!');

      // Confirm approval
      const confirmButton = screen.getByRole('button', { name: /confirm/i });
      await user.click(confirmButton);

      // Wait for success feedback
      await waitFor(() => {
        expect(screen.getByText(/job approved successfully/i)).toBeInTheDocument();
      });

      // Verify modal closes
      await waitFor(() => {
        expect(screen.queryByRole('dialog')).not.toBeInTheDocument();
      });

      // Verify job status updated in UI (optimistic update)
      await waitFor(() => {
        expect(screen.getByText('approved')).toBeInTheDocument();
      });
    });

    it('successfully rejects a job with required reason', async () => {
      const user = userEvent.setup();
      render(<Dashboard />);

      // Wait for jobs to load
      await waitFor(() => {
        expect(screen.getByText('Review Marketing Campaign Assets')).toBeInTheDocument();
      });

      // Click reject button
      const rejectButton = screen.getByRole('button', { name: /reject/i });
      await user.click(rejectButton);

      // Verify rejection modal opens
      await waitFor(() => {
        expect(screen.getByRole('dialog')).toBeInTheDocument();
        expect(screen.getByText(/reject job/i)).toBeInTheDocument();
      });

      // Try to confirm without reason (should be prevented)
      const confirmButton = screen.getByRole('button', { name: /confirm/i });
      expect(confirmButton).toBeDisabled();

      // Add rejection reason
      const reasonField = screen.getByLabelText(/rejection reason/i);
      await user.type(reasonField, 'Content does not meet brand guidelines');

      // Confirm button should now be enabled
      await waitFor(() => {
        expect(confirmButton).toBeEnabled();
      });

      // Confirm rejection
      await user.click(confirmButton);

      // Wait for success feedback
      await waitFor(() => {
        expect(screen.getByText(/job rejected successfully/i)).toBeInTheDocument();
      });
    });
  });

  describe('Status Filtering Integration', () => {
    it('filters jobs by status and maintains state', async () => {
      const user = userEvent.setup();
      render(<Dashboard />);

      // Wait for initial load
      await waitFor(() => {
        expect(screen.getByText('All Jobs')).toBeInTheDocument();
      });

      // Click on Pending tab
      const pendingTab = screen.getByRole('tab', { name: /pending/i });
      await user.click(pendingTab);

      // Verify only pending jobs are shown
      await waitFor(() => {
        const pendingJobs = screen.getAllByText('pending');
        expect(pendingJobs.length).toBeGreaterThan(0);
        expect(screen.queryByText('approved')).not.toBeInTheDocument();
      });

      // Switch to Approved tab
      const approvedTab = screen.getByRole('tab', { name: /approved/i });
      await user.click(approvedTab);

      // Verify only approved jobs are shown
      await waitFor(() => {
        expect(screen.getByText('approved')).toBeInTheDocument();
        expect(screen.queryByText('pending')).not.toBeInTheDocument();
      });
    });
  });

  describe('Real-time Updates Simulation', () => {
    it('handles concurrent job status changes', async () => {
      const user = userEvent.setup();
      render(<Dashboard />);

      // Wait for initial load
      await waitFor(() => {
        expect(screen.getByText('Review Marketing Campaign Assets')).toBeInTheDocument();
      });

      // Simulate external status change via API
      server.use(
        rest.get('/api/jobs', (req, res, ctx) => {
          const updatedJobs = sampleJobs.sampleJobs.map(job => 
            job.id === 'job-001' 
              ? { ...job, status: 'approved' }
              : job
          );
          return res(ctx.json({ jobs: updatedJobs, total: updatedJobs.length }));
        })
      );

      // Trigger a refresh (simulating real-time update)
      const refreshButton = screen.getByRole('button', { name: /refresh/i });
      if (refreshButton) {
        await user.click(refreshButton);
      }

      // Verify status change is reflected
      await waitFor(() => {
        expect(screen.getByText('approved')).toBeInTheDocument();
      });
    });
  });

  describe('Error Handling', () => {
    it('handles API errors gracefully during approval', async () => {
      const user = userEvent.setup();
      
      // Mock API failure
      server.use(
        rest.post('/api/jobs/:id/approve', (req, res, ctx) => {
          return res(ctx.status(500), ctx.json({ error: 'Server error' }));
        })
      );

      render(<Dashboard />);

      // Wait for jobs to load
      await waitFor(() => {
        expect(screen.getByText('Review Marketing Campaign Assets')).toBeInTheDocument();
      });

      // Attempt approval
      const approveButton = screen.getByRole('button', { name: /approve/i });
      await user.click(approveButton);

      // Confirm in modal
      await waitFor(() => {
        expect(screen.getByRole('dialog')).toBeInTheDocument();
      });

      const confirmButton = screen.getByRole('button', { name: /confirm/i });
      await user.click(confirmButton);

      // Verify error message is shown
      await waitFor(() => {
        expect(screen.getByText(/error/i)).toBeInTheDocument();
      });

      // Verify job status hasn't changed (failed optimistic update)
      expect(screen.getByText('pending')).toBeInTheDocument();
    });

    it('handles network timeout gracefully', async () => {
      const user = userEvent.setup();
      
      // Mock delayed response
      server.use(
        rest.post('/api/jobs/:id/approve', (req, res, ctx) => {
          return res(ctx.delay(15000)); // 15 second delay
        })
      );

      render(<Dashboard />);

      // Wait for jobs to load
      await waitFor(() => {
        expect(screen.getByText('Review Marketing Campaign Assets')).toBeInTheDocument();
      });

      // Attempt approval
      const approveButton = screen.getByRole('button', { name: /approve/i });
      await user.click(approveButton);

      // Confirm in modal
      await waitFor(() => {
        expect(screen.getByRole('dialog')).toBeInTheDocument();
      });

      const confirmButton = screen.getByRole('button', { name: /confirm/i });
      await user.click(confirmButton);

      // Verify loading state is shown
      await waitFor(() => {
        expect(screen.getByText(/processing/i)).toBeInTheDocument();
      });
    });
  });

  describe('Accessibility Integration', () => {
    it('maintains keyboard navigation throughout workflow', async () => {
      const user = userEvent.setup();
      render(<Dashboard />);

      // Wait for load
      await waitFor(() => {
        expect(screen.getByText('Review Marketing Campaign Assets')).toBeInTheDocument();
      });

      // Navigate via keyboard
      await user.keyboard('[Tab]'); // Focus first interactive element
      await user.keyboard('[Enter]'); // Activate approve

      // Verify modal opens and is focusable
      await waitFor(() => {
        const modal = screen.getByRole('dialog');
        expect(modal).toBeInTheDocument();
        expect(modal).toHaveFocus();
      });

      // Navigate within modal
      await user.keyboard('[Tab]'); // Focus to notes field
      await user.keyboard('[Tab]'); // Focus to cancel button
      await user.keyboard('[Tab]'); // Focus to confirm button

      // Close modal with Escape
      await user.keyboard('[Escape]');

      // Verify modal closes
      await waitFor(() => {
        expect(screen.queryByRole('dialog')).not.toBeInTheDocument();
      });
    });
  });
}); 