// Unit test example for JobCard component
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
      title: 'Test Job Title',
      status: 'pending' as const,
      priority: 'medium' as const,
      description: 'Test job description'
    }),
    onApprove: mockOnApprove,
    onReject: mockOnReject,
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Rendering', () => {
    it('displays job title and basic information', () => {
      render(<JobCard {...defaultProps} />);
      
      expect(screen.getByText('Test Job Title')).toBeInTheDocument();
      expect(screen.getByText('pending')).toBeInTheDocument();
      expect(screen.getByText('medium')).toBeInTheDocument();
      expect(screen.getByText('Test job description')).toBeInTheDocument();
    });

    it('shows action buttons for pending jobs', () => {
      render(<JobCard {...defaultProps} />);
      
      expect(screen.getByRole('button', { name: /approve/i })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /reject/i })).toBeInTheDocument();
    });

    it('does not show action buttons for non-pending jobs', () => {
      const approvedJob = createMockJob({ status: 'approved' });
      render(<JobCard {...defaultProps} job={approvedJob} />);
      
      expect(screen.queryByRole('button', { name: /approve/i })).not.toBeInTheDocument();
      expect(screen.queryByRole('button', { name: /reject/i })).not.toBeInTheDocument();
    });

    it('hides action buttons when showActions is false', () => {
      render(<JobCard {...defaultProps} showActions={false} />);
      
      expect(screen.queryByRole('button', { name: /approve/i })).not.toBeInTheDocument();
      expect(screen.queryByRole('button', { name: /reject/i })).not.toBeInTheDocument();
    });

    it('applies compact styling when compact prop is true', () => {
      const { container } = render(<JobCard {...defaultProps} compact={true} />);
      
      const card = container.querySelector('[class*="p-3"]');
      expect(card).toBeInTheDocument();
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
      
      expect(mockOnReject).toHaveBeenCalledWith('test-job-1', '');
      expect(mockOnReject).toHaveBeenCalledTimes(1);
    });

    it('handles missing callback functions gracefully', async () => {
      const user = userEvent.setup();
      render(<JobCard {...defaultProps} onApprove={undefined} onReject={undefined} />);
      
      const approveButton = screen.getByRole('button', { name: /approve/i });
      
      // Should not throw error when clicking
      await expect(user.click(approveButton)).resolves.not.toThrow();
    });
  });

  describe('Status Display', () => {
    it.each([
      ['pending', 'amber'],
      ['approved', 'green'], 
      ['rejected', 'red'],
      ['completed', 'gray']
    ])('displays correct color for %s status', (status, expectedColor) => {
      const job = createMockJob({ status: status as any });
      const { container } = render(<JobCard {...defaultProps} job={job} />);
      
      const statusBadge = container.querySelector(`[class*="${expectedColor}"]`);
      expect(statusBadge).toBeInTheDocument();
    });
  });

  describe('Priority Display', () => {
    it.each([
      ['urgent', 'red'],
      ['high', 'orange'],
      ['medium', 'yellow'],
      ['low', 'green']
    ])('displays correct color for %s priority', (priority, expectedColor) => {
      const job = createMockJob({ priority: priority as any });
      const { container } = render(<JobCard {...defaultProps} job={job} />);
      
      const priorityElement = container.querySelector(`[class*="text-${expectedColor}"]`);
      expect(priorityElement).toBeInTheDocument();
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
      
      // Tab to approve button
      await user.tab();
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
        status: 'pending' as const,
        // Missing title, description, etc.
      };
      
      expect(() => {
        render(<JobCard {...defaultProps} job={incompleteJob as any} />);
      }).not.toThrow();
    });

    it('handles long job titles appropriately', () => {
      const longTitleJob = createMockJob({
        title: 'This is a very long job title that should be truncated or handled appropriately to prevent layout issues'
      });
      
      const { container } = render(<JobCard {...defaultProps} job={longTitleJob} />);
      const titleElement = container.querySelector('[class*="line-clamp"]');
      expect(titleElement).toBeInTheDocument();
    });
  });
}); 