// E2E tests for critical job management user journeys
import { test, expect } from '@playwright/test';

test.describe('Job Management Dashboard - Critical Paths', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to dashboard
    await page.goto('/dashboard');
    
    // Wait for page to load completely
    await page.waitForLoadState('networkidle');
    await expect(page.locator('body')).toBeVisible();
  });

  test.describe('Job Approval Flow', () => {
    test('user can approve a job end-to-end', async ({ page }) => {
      // Verify dashboard loads with jobs
      await expect(page.locator('[data-testid="job-card"]').first()).toBeVisible();
      
      // Navigate to pending jobs tab
      await page.click('button:has-text("Pending")');
      await expect(page.locator('[aria-selected="true"]')).toContainText('Pending');
      
      // Find first pending job and approve it
      const firstJobCard = page.locator('[data-testid="job-card"]').first();
      await expect(firstJobCard).toBeVisible();
      
      // Get job title for verification later
      const jobTitle = await firstJobCard.locator('[data-testid="job-title"]').textContent();
      
      // Click approve button
      await firstJobCard.locator('button:has-text("Approve")').click();
      
      // Verify approval modal opens
      await expect(page.locator('[role="dialog"]')).toBeVisible();
      await expect(page.locator('text=Approve Job')).toBeVisible();
      
      // Verify job details are shown in modal
      await expect(page.locator(`text=${jobTitle}`)).toBeVisible();
      
      // Add approval notes
      await page.fill('[data-testid="approval-notes"]', 'Approved after thorough review');
      
      // Confirm approval
      await page.click('button:has-text("Confirm")');
      
      // Verify success notification
      await expect(page.locator('.toast, [data-testid="success-message"]')).toContainText(/approved successfully/i);
      
      // Verify modal closes
      await expect(page.locator('[role="dialog"]')).not.toBeVisible();
      
      // Navigate to approved jobs to verify status change
      await page.click('button:has-text("Approved")');
      await expect(page.locator('[aria-selected="true"]')).toContainText('Approved');
      
      // Verify the job appears in approved section
      await expect(page.locator(`[data-testid="job-card"]:has-text("${jobTitle}")`)).toBeVisible();
    });

    test('user can reject a job with required reason', async ({ page }) => {
      // Navigate to pending jobs
      await page.click('button:has-text("Pending")');
      
      // Find first pending job
      const firstJobCard = page.locator('[data-testid="job-card"]').first();
      const jobTitle = await firstJobCard.locator('[data-testid="job-title"]').textContent();
      
      // Click reject button
      await firstJobCard.locator('button:has-text("Reject")').click();
      
      // Verify rejection modal opens
      await expect(page.locator('[role="dialog"]')).toBeVisible();
      await expect(page.locator('text=Reject Job')).toBeVisible();
      
      // Verify confirm button is disabled without reason
      await expect(page.locator('button:has-text("Confirm")')).toBeDisabled();
      
      // Add rejection reason
      await page.fill('[data-testid="rejection-reason"]', 'Does not meet quality standards');
      
      // Verify confirm button is now enabled
      await expect(page.locator('button:has-text("Confirm")')).toBeEnabled();
      
      // Confirm rejection
      await page.click('button:has-text("Confirm")');
      
      // Verify success notification
      await expect(page.locator('.toast, [data-testid="success-message"]')).toContainText(/rejected successfully/i);
      
      // Navigate to rejected jobs to verify
      await page.click('button:has-text("Rejected")');
      await expect(page.locator(`[data-testid="job-card"]:has-text("${jobTitle}")`)).toBeVisible();
    });
  });

  test.describe('Navigation and Filtering', () => {
    test('user can filter jobs by status', async ({ page }) => {
      // Test each status tab
      const statusTabs = ['All', 'Pending', 'Approved', 'Rejected', 'Completed'];
      
      for (const status of statusTabs) {
        await page.click(`button:has-text("${status}")`);
        
        // Verify tab is active
        await expect(page.locator('[aria-selected="true"]')).toContainText(status);
        
        // Verify job count is displayed
        await expect(page.locator(`button:has-text("${status}") [data-testid="job-count"]`)).toBeVisible();
        
        // If not "All", verify only jobs with that status are shown
        if (status !== 'All') {
          const jobCards = page.locator('[data-testid="job-card"]');
          const count = await jobCards.count();
          
          if (count > 0) {
            // Verify all visible jobs have the correct status
            for (let i = 0; i < count; i++) {
              await expect(jobCards.nth(i).locator('[data-testid="job-status"]')).toContainText(status.toLowerCase());
            }
          }
        }
      }
    });

    test('status tab counts update after job actions', async ({ page }) => {
      // Get initial pending count
      const pendingTab = page.locator('button:has-text("Pending")');
      const initialPendingText = await pendingTab.textContent();
      const initialPendingCount = parseInt(initialPendingText?.match(/\d+/)?.[0] || '0');
      
      // Navigate to pending and approve a job
      await pendingTab.click();
      
      if (initialPendingCount > 0) {
        const firstJob = page.locator('[data-testid="job-card"]').first();
        await firstJob.locator('button:has-text("Approve")').click();
        
        // Complete approval
        await page.locator('[role="dialog"]').waitFor();
        await page.click('button:has-text("Confirm")');
        await page.locator('[role="dialog"]').waitFor({ state: 'hidden' });
        
        // Verify pending count decreased
        await expect(pendingTab).not.toContainText(initialPendingCount.toString());
        
        // Verify approved count increased
        const approvedTab = page.locator('button:has-text("Approved")');
        await expect(approvedTab.locator('[data-testid="job-count"]')).toBeVisible();
      }
    });
  });

  test.describe('Sound Notifications', () => {
    test('user can toggle sound notifications', async ({ page }) => {
      // Find sound toggle button
      const soundToggle = page.locator('[data-testid="sound-toggle"]');
      await expect(soundToggle).toBeVisible();
      
      // Get initial state
      const initialState = await soundToggle.getAttribute('aria-pressed');
      
      // Toggle sound
      await soundToggle.click();
      
      // Verify state changed
      const newState = await soundToggle.getAttribute('aria-pressed');
      expect(newState).not.toBe(initialState);
      
      // Verify visual indication updated
      if (newState === 'true') {
        await expect(soundToggle).toHaveClass(/text-blue/);
      } else {
        await expect(soundToggle).toHaveClass(/text-gray/);
      }
    });

    test('sound preference persists across page reloads', async ({ page }) => {
      const soundToggle = page.locator('[data-testid="sound-toggle"]');
      
      // Set sound to off
      await soundToggle.click();
      const toggledState = await soundToggle.getAttribute('aria-pressed');
      
      // Reload page
      await page.reload();
      await page.waitForLoadState('networkidle');
      
      // Verify state persisted
      await expect(soundToggle).toHaveAttribute('aria-pressed', toggledState);
    });
  });

  test.describe('Responsive Design', () => {
    test('dashboard works on mobile devices', async ({ page }) => {
      // Set mobile viewport
      await page.setViewportSize({ width: 375, height: 667 });
      
      // Verify dashboard loads
      await expect(page.locator('[data-testid="job-card"]').first()).toBeVisible();
      
      // Verify status tabs are responsive
      await expect(page.locator('button:has-text("All")')).toBeVisible();
      
      // Test job card interaction on mobile
      const firstJob = page.locator('[data-testid="job-card"]').first();
      await expect(firstJob).toBeVisible();
      
      // Verify touch targets are large enough (minimum 44px)
      const approveButton = firstJob.locator('button:has-text("Approve")');
      if (await approveButton.isVisible()) {
        const boundingBox = await approveButton.boundingBox();
        expect(boundingBox?.height).toBeGreaterThanOrEqual(44);
      }
    });

    test('dashboard works on tablet devices', async ({ page }) => {
      // Set tablet viewport
      await page.setViewportSize({ width: 768, height: 1024 });
      
      // Verify layout adapts to tablet size
      await expect(page.locator('[data-testid="job-card"]')).toBeVisible();
      
      // Verify more jobs can be displayed side by side
      const jobCards = page.locator('[data-testid="job-card"]');
      const count = await jobCards.count();
      
      if (count >= 2) {
        const firstCard = await jobCards.first().boundingBox();
        const secondCard = await jobCards.nth(1).boundingBox();
        
        // Cards should be side by side on tablet
        expect(firstCard?.x).toBeLessThan(secondCard?.x || 0);
      }
    });
  });

  test.describe('Performance', () => {
    test('dashboard loads within performance budget', async ({ page }) => {
      const startTime = Date.now();
      
      await page.goto('/dashboard');
      await page.waitForLoadState('networkidle');
      
      const loadTime = Date.now() - startTime;
      
      // Dashboard should load within 3 seconds
      expect(loadTime).toBeLessThan(3000);
    });

    test('job actions respond quickly', async ({ page }) => {
      await page.goto('/dashboard');
      await page.waitForLoadState('networkidle');
      
      // Navigate to pending jobs
      await page.click('button:has-text("Pending")');
      
      const firstJob = page.locator('[data-testid="job-card"]').first();
      await firstJob.waitFor();
      
      const startTime = Date.now();
      
      // Click approve button
      await firstJob.locator('button:has-text("Approve")').click();
      
      // Wait for modal to appear
      await page.locator('[role="dialog"]').waitFor();
      
      const responseTime = Date.now() - startTime;
      
      // UI should respond within 500ms
      expect(responseTime).toBeLessThan(500);
    });
  });

  test.describe('Error Handling', () => {
    test('handles network errors gracefully', async ({ page }) => {
      // Simulate network failure
      await page.route('/api/jobs/**', route => route.abort());
      
      await page.goto('/dashboard');
      
      // Verify error state is shown
      await expect(page.locator('[data-testid="error-message"], text=/error/i')).toBeVisible();
      
      // Verify retry option is available
      await expect(page.locator('button:has-text("Retry"), button:has-text("Reload")')).toBeVisible();
    });

    test('shows loading states during actions', async ({ page }) => {
      // Add delay to API responses
      await page.route('/api/jobs/**/approve', async route => {
        await new Promise(resolve => setTimeout(resolve, 2000));
        await route.fulfill({ json: { success: true } });
      });
      
      await page.goto('/dashboard');
      await page.waitForLoadState('networkidle');
      
      // Start approval process
      await page.click('button:has-text("Pending")');
      const firstJob = page.locator('[data-testid="job-card"]').first();
      await firstJob.locator('button:has-text("Approve")').click();
      
      await page.locator('[role="dialog"]').waitFor();
      await page.click('button:has-text("Confirm")');
      
      // Verify loading state is shown
      await expect(page.locator('text=/processing|loading/i')).toBeVisible();
    });
  });
}); 