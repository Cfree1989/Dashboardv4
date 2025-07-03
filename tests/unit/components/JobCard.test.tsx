// Unit test example for JobCard component
import React from 'react';
import { render, screen } from '../../../tests/config/test-utils';
import { JobCard } from '../../../Project Information/v0/components/dashboard/job-card';
import { createMockJob, testAccessibility } from '../../config/test-utils';
import userEvent from '@testing-library/user-event';

describe('JobCard', () => {
  const mockOnApprove = jest.fn();
  const mockOnReject = jest.fn();
  
  const defaultProps = {
    job: createMockJob({
      id: 'test-job-1',
      displayName: 'Test Job Title',
      status: 'UPLOADED' as const,
      studentName: 'Test Student'
    }),
    currentStatus: 'UPLOADED' as const,
    onApprove: mockOnApprove,
    onReject: mockOnReject,
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Rendering', () => {
    it('displays job title and basic information', () => {
      render(<JobCard {...defaultProps} />);
      
      expect(screen.getAllByText('Test Student')).toHaveLength(2); // Header and details section
      expect(screen.getByText('Test Job Title')).toBeInTheDocument();
    });

    it('shows action buttons for UPLOADED jobs', () => {
      render(<JobCard {...defaultProps} />);
      
      expect(screen.getByRole('button', { name: /approve/i })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /reject/i })).toBeInTheDocument();
    });

    it('does not show action buttons for non-UPLOADED jobs', () => {
      const completedJob = createMockJob({ status: 'COMPLETED' });
      render(<JobCard {...defaultProps} job={completedJob} currentStatus="COMPLETED" />);
      
      expect(screen.queryByRole('button', { name: /approve/i })).not.toBeInTheDocument();
      expect(screen.queryByRole('button', { name: /reject/i })).not.toBeInTheDocument();
    });

    it('shows expand/collapse button', () => {
      render(<JobCard {...defaultProps} />);
      
      expect(screen.getByRole('button', { name: /show more/i })).toBeInTheDocument();
    });
  });

  describe('User Interactions', () => {
    it('calls onApprove when approve button is clicked', async () => {
      const user = userEvent.setup();
      render(<JobCard {...defaultProps} />);
      
      const approveButton = screen.getByRole('button', { name: /approve/i });
      await user.click(approveButton);
      
      expect(mockOnApprove).toHaveBeenCalledWith('test-job-1');
      expect(mockOnApprove).toHaveBeenCalledTimes(1);
    });

    it('calls onReject when reject button is clicked', async () => {
      const user = userEvent.setup();
      render(<JobCard {...defaultProps} />);
      
      const rejectButton = screen.getByRole('button', { name: /reject/i });
      await user.click(rejectButton);
      
      expect(mockOnReject).toHaveBeenCalledWith('test-job-1');
      expect(mockOnReject).toHaveBeenCalledTimes(1);
    });

    it('handles missing callback functions gracefully', async () => {
      const user = userEvent.setup();
      const noop = () => {};
      render(<JobCard {...defaultProps} onApprove={noop} onReject={noop} />);
      
      const approveButton = screen.getByRole('button', { name: /approve/i });
      
      // Should not throw error when clicking
      await expect(user.click(approveButton)).resolves.not.toThrow();
    });
  });

  describe('Job Information Display', () => {
    it('displays job age with appropriate color coding', () => {
      const { container } = render(<JobCard {...defaultProps} />);
      
      // Should show time elapsed
      expect(container).toHaveTextContent(/ago/);
    });
  });

  describe('Accessibility', () => {
    it('meets WCAG accessibility standards', async () => {
      const { container } = render(<JobCard {...defaultProps} />);
      await testAccessibility(container);
    });

    it('has proper ARIA labels for buttons', () => {
      render(<JobCard {...defaultProps} />);
      
      const approveButton = screen.getByRole('button', { name: /approve/i });
      const rejectButton = screen.getByRole('button', { name: /reject/i });
      
      expect(approveButton).toHaveAccessibleName('Approve');
      expect(rejectButton).toHaveAccessibleName('Reject');
    });

    it('supports keyboard navigation', async () => {
      const user = userEvent.setup();
      render(<JobCard {...defaultProps} />);
      
      // Tab through all focusable elements
      await user.tab(); // Mark as Reviewed button
      await user.tab(); // Show More button  
      await user.tab(); // Approve button
      expect(screen.getByRole('button', { name: /approve/i })).toHaveFocus();
      
      // Tab to reject button
      await user.tab();
      expect(screen.getByRole('button', { name: /reject/i })).toHaveFocus();
    });
  });

  describe('Performance', () => {
    it('renders within performance budget', async () => {
      const start = performance.now();
      render(<JobCard {...defaultProps} />);
      const end = performance.now();
      
      expect(end - start).toBeLessThan(100); // 100ms budget
    });
  });

  describe('Error Handling', () => {
    it('handles missing job properties gracefully', () => {
      const incompleteJob = {
        id: 'incomplete-job',
        studentName: 'Test Student',
        studentEmail: 'test@example.com',
        discipline: 'Engineering',
        classNumber: 'ENG101',
        originalFilename: 'test.stl',
        displayName: 'Test Job',
        filePath: '/path/to/file.stl',
        metadataPath: '/path/to/metadata.json',
        status: 'UPLOADED' as const,
        printer: null,
        color: null,
        material: null,
        weightG: null,
        timeHours: null,
        costUsd: null,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
        staffViewedAt: null,
        notes: null,
      };
      
      expect(() => {
        render(<JobCard {...defaultProps} job={incompleteJob} />);
      }).not.toThrow();
    });

    it('handles long job titles appropriately', () => {
      const longTitleJob = createMockJob({
        displayName: 'This is a very long job title that should be truncated or handled appropriately to prevent layout issues'
      });
      
      const { container } = render(<JobCard {...defaultProps} job={longTitleJob} />);
      const titleElement = container.querySelector('[class*="truncate"]');
      expect(titleElement).toBeInTheDocument();
    });
  });
}); 